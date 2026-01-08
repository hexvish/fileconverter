from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                               QTableWidgetItem, QPushButton, QHeaderView, 
                               QProgressBar, QLabel, QHBoxLayout)
from PySide6.QtCore import Qt
import os

from src.core.worker import ConversionWorker

class ProgressWindow(QWidget):
    def __init__(self, auto_start=True):
        super().__init__()
        self.setWindowTitle("Conversion Progress")
        self.resize(600, 400)
        self.auto_start_on_show = auto_start
        
        self.layout = QVBoxLayout(self)
        
        # Header info
        self.info_label = QLabel("Waiting to start...")
        self.layout.addWidget(self.info_label)

        # File List Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Filename", "Preset", "Progress", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Buttons
        self.btn_layout = QHBoxLayout()
        self.layout.addLayout(self.btn_layout)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_worker)
        self.start_btn.setVisible(not self.auto_start_on_show)
        self.btn_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("Cancel All")
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.btn_layout.addWidget(self.cancel_btn)
        
        self.worker = None
        self.jobs = []
        self.file_row_map = {} # Maps filename to row index

    def add_file(self, filename: str, preset_name: str, full_path: str = None, custom_config: dict = None):
        if not full_path and os.path.isfile(filename):
             full_path = filename
             filename = os.path.basename(filename)

        row = self.table.rowCount()
        self.table.insertRow(row)
        
        self.table.setItem(row, 0, QTableWidgetItem(filename))
        self.table.setItem(row, 1, QTableWidgetItem(preset_name))
        
        # Progress Bar
        pbar = QProgressBar()
        pbar.setRange(0, 100)
        pbar.setValue(0)
        self.table.setCellWidget(row, 2, pbar)
        
        self.table.setItem(row, 3, QTableWidgetItem("Pending"))
        
        if full_path:
            job = {'path': full_path, 'preset_name': preset_name}
            if custom_config:
                job['custom_config'] = custom_config
            self.jobs.append(job)
            self.file_row_map[full_path] = row
        else:
            # Error state if no valid path
            self.table.setItem(row, 3, QTableWidgetItem("Error: path missing"))

    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()
        if self.auto_start_on_show:
            self.start_worker()

    def start_worker(self):
        self.start_btn.setVisible(False)
        self.info_label.setText("Conversion in progress...")
        self.worker = ConversionWorker(self.jobs)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.update_status)
        self.worker.all_finished_signal.connect(self.on_all_finished)
        self.worker.start()

    def update_progress(self, file_path, progress):
        row = self.file_row_map.get(file_path)
        if row is not None:
             pbar = self.table.cellWidget(row, 2)
             if pbar:
                 pbar.setValue(progress)

    def update_status(self, file_path, success, message):
        row = self.file_row_map.get(file_path)
        if row is not None:
            self.table.setItem(row, 3, QTableWidgetItem(message))
            
    def on_all_finished(self):
        self.info_label.setText("All conversions finished.")
        self.cancel_btn.setText("Close")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.close)

    def cancel_conversion(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        self.close()
