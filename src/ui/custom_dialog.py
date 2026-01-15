from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                               QSpinBox, QComboBox, QDialogButtonBox, QLabel)
from PySide6.QtCore import Qt

class CustomPresetDialog(QDialog):
    def __init__(self, file_type_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Settings")
        self.resize(300, 200)
        
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, 10000)
        self.width_spin.setSpecialValueText("Auto")
        self.width_spin.setValue(0) # 0 means Auto
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, 10000)
        self.height_spin.setSpecialValueText("Auto")
        self.height_spin.setValue(0)
        
        self.format_combo = QComboBox()
        
        # Populate formats based on type
        if file_type_name == "IMAGE":
            self.format_combo.addItems(["jpg", "png", "webp", "pdf"])
            self.form_layout.addRow("Width (px):", self.width_spin)
            self.form_layout.addRow("Height (px):", self.height_spin)
        elif file_type_name == "VIDEO":
            self.format_combo.addItems(["mp4", "webm", "avi", "mp3", "wav"])
            # Videos usually care about height (480p, 720p) more often, but let's offer both
            self.form_layout.addRow("Width (px):", self.width_spin)
            self.form_layout.addRow("Height (px):", self.height_spin)
        elif file_type_name == "AUDIO":
            self.format_combo.addItems(["mp3", "wav", "ogg", "flac"])
            # Audio doesn't have dimensions
        
        self.form_layout.addRow("Target Format:", self.format_combo)
        
        self.layout.addLayout(self.form_layout)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.layout.addWidget(self.button_box)
        
    def get_config(self):
        config = {
            "action": "convert", # default action
            "format": self.format_combo.currentText()
        }
        
        w = self.width_spin.value()
        h = self.height_spin.value()
        
        if w > 0 or h > 0:
            config["action"] = "resize" # Should imply convert as well usually, but engine handles it
            if w > 0:
                config["width"] = w
            if h > 0:
                config["height"] = h
                
        return config
