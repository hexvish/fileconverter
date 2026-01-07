from PySide6.QtCore import QThread, Signal
import os
from src.core.file_detector import FileType, FileDetector
from src.core.image_engine import ImageEngine
from src.core.video_engine import VideoEngine
from src.core.audio_engine import AudioEngine
from src.core.pdf_engine import PdfEngine
from src.core.preset_manager import PresetManager

class ConversionWorker(QThread):
    progress_signal = Signal(str, int)  # file_path, progress (0-100)
    finished_signal = Signal(str, bool, str)  # file_path, success, message
    all_finished_signal = Signal()

    def __init__(self, job_list):
        """
        job_list: list of dicts { 'path': str, 'preset_name': str }
        """
        super().__init__()
        self.job_list = job_list
        self.is_running = True
        self.current_process_holder = [None] # Mutable list to store current Popen object

    def run(self):
        total_files = len(self.job_list)
        
        for index, job in enumerate(self.job_list):
            if not self.is_running:
                break
                
            input_path = job['path']
            preset_name = job['preset_name']
            
            file_type = FileDetector.detect(input_path)
            presets = PresetManager.get_presets(file_type)
            preset_data = presets.get(preset_name)

            if not preset_data:
                self.finished_signal.emit(input_path, False, "Invalid Preset")
                continue

            # Generate Output Path
            input_dir = os.path.dirname(input_path)
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            
            # Determine new extension if format change
            if preset_data.get("action") == "convert" and "format" in preset_data:
                new_ext = "." + preset_data["format"]
            else:
                new_ext = ext
                
            output_path = os.path.join(input_dir, f"{name}_converted{new_ext}")
            
            # Handle duplicates: append (1), (2), etc.
            counter = 1
            base_output_path = output_path
            while os.path.exists(output_path):
                name_no_ext, ext_part = os.path.splitext(base_output_path)
                output_path = f"{name_no_ext}({counter}){ext_part}"
                counter += 1

            # Notify start
            self.progress_signal.emit(input_path, 0)
            
            success = False
            error_msg = ""
            
            # Reset process holder for this job
            self.current_process_holder[0] = None

            if file_type == FileType.IMAGE:
                success = ImageEngine.convert(input_path, output_path, preset_data, self.current_process_holder)
                if not success:
                    error_msg = "ImageMagick failed"
            elif file_type == FileType.VIDEO:
                # Video conversion or extraction
                # If target format is audio (mp3, wav), we use AudioEngine logic? 
                # Actually FFmpeg (VideoEngine) can handle it, but using AudioEngine might be cleaner/more specialized?
                # VideoEngine uses 'ffmpeg -i ...' which works for extraction too.
                # But let's check: VideoEngine is wired to use 'video' presets mostly.
                # If we use VideoEngine for extraction, it should work fine if preset format is mp3.
                
                # However, we must also support FileType.AUDIO inputs now.
                
                progress_cb = lambda p: self.progress_signal.emit(input_path, p)
                success = VideoEngine.convert(input_path, output_path, preset_data, self.current_process_holder, progress_cb)
                if not success:
                    error_msg = "FFmpeg failed"
            elif file_type == FileType.AUDIO:
                progress_cb = lambda p: self.progress_signal.emit(input_path, p)
                success = AudioEngine.convert(input_path, output_path, preset_data, self.current_process_holder, progress_cb)
                if not success:
                    error_msg = "FFmpeg Audio failed"
            elif file_type == FileType.PDF:
                if preset_data.get("action") == "compress":
                    success = PdfEngine.compress(input_path, output_path, preset_data, self.current_process_holder)
                    if not success:
                        error_msg = "Ghostscript compression failed"
                else:
                     error_msg = "Action not supported for PDF"
            else:
                # Placeholder for other engines
                success = True # Mock success for non-implemented types
                error_msg = "Not implemented yet"

            # Check if stopped during process
            if not self.is_running:
                self.finished_signal.emit(input_path, False, "Cancelled")
                continue

            if success:
                self.progress_signal.emit(input_path, 100)
                self.finished_signal.emit(input_path, True, "Completed")
            else:
                self.finished_signal.emit(input_path, False, error_msg)

        self.all_finished_signal.emit()

    def stop(self):
        self.is_running = False
        # Kill current process if it exists
        if self.current_process_holder[0]:
            try:
                self.current_process_holder[0].kill()
            except Exception as e:
                print(f"Error killing process: {e}")
