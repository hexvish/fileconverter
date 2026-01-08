from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLabel,
                               QDialogButtonBox)
from PySide6.QtCore import Qt

class MediaInfoWindow(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Media Info - {data.get('file', 'Unknown')}")
        self.resize(500, 400)
        
        self.layout = QVBoxLayout(self)
        
        # General Info Table
        self.gen_label = QLabel("<b>General</b>")
        self.layout.addWidget(self.gen_label)
        
        self.gen_table = QTableWidget()
        self.gen_table.setColumnCount(2)
        self.gen_table.verticalHeader().setVisible(False)
        self.gen_table.horizontalHeader().setVisible(False)
        self.gen_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        gen_keys = [
            ("File", data.get("file")),
            ("Path", data.get("path")),
            ("Size", data.get("size_str")),
            ("Format", data.get("format")),
            ("Duration", f"{float(data.get('duration', 0)):.2f} sec" if data.get('duration') != "N/A" else "N/A")
        ]
        
        self.populate_table(self.gen_table, gen_keys)
        self.layout.addWidget(self.gen_table)
        
        # Streams
        streams = data.get("streams", [])
        for stream in streams:
            sType = stream.get("type", "Unknown").title()
            label = QLabel(f"<b>{sType} Stream #{stream.get('index')}</b>")
            self.layout.addWidget(label)
            
            stream_table = QTableWidget()
            stream_table.setColumnCount(2)
            stream_table.verticalHeader().setVisible(False)
            stream_table.horizontalHeader().setVisible(False)
            stream_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            
            s_keys = [("Codec", stream.get("codec"))]
            
            if sType == "Video":
                s_keys.append(("Resolution", f"{stream.get('width')}x{stream.get('height')}"))
                s_keys.append(("Frame Rate", stream.get("fps")))
            elif sType == "Audio":
                s_keys.append(("Channels", str(stream.get("channels"))))
                s_keys.append(("Sample Rate", f"{stream.get('sample_rate')} Hz"))
                
            self.populate_table(stream_table, s_keys)
            self.layout.addWidget(stream_table)
            
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.close)
        self.layout.addWidget(self.button_box)
        
    def populate_table(self, table, data_list):
        table.setRowCount(len(data_list))
        for i, (key, value) in enumerate(data_list):
            item_k = QTableWidgetItem(str(key))
            item_k.setFlags(Qt.ItemIsEnabled)
            item_k.setBackground(Qt.lightGray)
            
            item_v = QTableWidgetItem(str(value))
            item_v.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            
            table.setItem(i, 0, item_k)
            table.setItem(i, 1, item_v)
        
        # Resize height to fit content
        total_height = 0 
        for i in range(table.rowCount()):
             total_height += table.rowHeight(i)
        table.setFixedHeight(total_height + 5)
