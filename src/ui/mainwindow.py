import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QListWidget, 
                               QListWidgetItem, QPushButton, QLabel, QMessageBox, QMenu)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QAction

from src.core.file_detector import FileDetector, FileType
from src.core.preset_manager import PresetManager
from src.ui.progresswindow import ProgressWindow
from src.ui.custom_dialog import CustomPresetDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileConverter")
        self.resize(500, 600)
        self.setAcceptDrops(True)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Drag & Drop Area / List
        self.label = QLabel("Drag & Drop files here\n(Right-click file to change preset)")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.file_list)

        # Start Button
        self.start_btn = QPushButton("Start Conversion")
        self.start_btn.clicked.connect(self.start_conversion)
        self.layout.addWidget(self.start_btn)

        # Keep reference to progress window
        self.progress_window = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.add_file(file_path)

    def add_file(self, file_path):
        file_type = FileDetector.detect(file_path)
        if file_type == FileType.UNKNOWN:
            return  # Skip unknown files

        # Get presets for this type
        presets = PresetManager.get_presets(file_type)
        if not presets:
            default_preset = "Default"
        else:
            # Default to the first preset found
            default_preset = list(presets.keys())[0]

        item = QListWidgetItem()
        item.setData(Qt.UserRole, file_path)
        item.setData(Qt.UserRole + 1, file_type)
        item.setData(Qt.UserRole + 2, default_preset)
        
        self.update_item_text(item)
        
        # Auto-select the new item for convenience (so Start Conversion only converts this)
        self.file_list.clearSelection()
        self.file_list.addItem(item)
        item.setSelected(True)

    def update_item_text(self, item):
        file_path = item.data(Qt.UserRole)
        file_type = item.data(Qt.UserRole + 1)
        preset = item.data(Qt.UserRole + 2)
        
        text = f"[{file_type.name}] {os.path.basename(file_path)}\n   -> {preset}"
        item.setText(text)

    def show_context_menu(self, pos):
        item = self.file_list.itemAt(pos)
        if not item:
            return

        file_type = item.data(Qt.UserRole + 1)
        presets = PresetManager.get_presets(file_type)
        
        menu = QMenu(self)
        for preset_name in presets.keys():
            action = QAction(preset_name, self)
            action.triggered.connect(lambda checked, n=preset_name, i=item: self.set_preset(i, n))
            menu.addAction(action)
        
        menu.exec(self.file_list.mapToGlobal(pos))

    def set_preset(self, item, preset_name):
        # Check if "Custom..." was selected
        if preset_name == "Custom...":
            file_type = item.data(Qt.UserRole + 1)
            dialog = CustomPresetDialog(file_type.name, self)
            if dialog.exec():
                custom_config = dialog.get_config()
                # Store custom config in a new UserRole
                item.setData(Qt.UserRole + 3, custom_config)
                # Update text to show it's custom
                fmt = custom_config.get("format", "unknown")
                w = custom_config.get("width", 0)
                h = custom_config.get("height", 0)
                
                details = f"({fmt})"
                if w > 0 or h > 0:
                     details = f"({fmt}, {w}x{h})"
                
                # We still store "Custom..." as the preset name key
                item.setData(Qt.UserRole + 2, preset_name)
                
                # Update visual text manually since update_item_text might need tweaking
                file_path = item.data(Qt.UserRole)
                text = f"[{file_type.name}] {os.path.basename(file_path)}\n   -> Custom {details}"
                item.setText(text)
                return

        # Normal preset selection
        item.setData(Qt.UserRole + 2, preset_name)
        # Clear custom data if any
        item.setData(Qt.UserRole + 3, None)
        self.update_item_text(item)

    def start_conversion(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No files", "Please add files first.")
            return

        items_to_process = self.file_list.selectedItems()
        if not items_to_process:
            # Fallback: if nothing selected, convert all
            items_to_process = [self.file_list.item(i) for i in range(self.file_list.count())]

        self.progress_window = ProgressWindow()
        
        for item in items_to_process:
            file_path = item.data(Qt.UserRole)
            preset_name = item.data(Qt.UserRole + 2)
            custom_config = item.data(Qt.UserRole + 3)
            
            if file_path:
                # Pass custom_config if it exists
                self.progress_window.add_file(os.path.basename(file_path), preset_name, file_path, custom_config)
            else:
                print("Error: Item missing file path")

        self.progress_window.show_window()
