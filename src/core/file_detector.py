import os
from enum import Enum, auto

class FileType(Enum):
    IMAGE = auto()
    VIDEO = auto()
    PDF = auto()
    AUDIO = auto()
    UNKNOWN = auto()

class FileDetector:
    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
    VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    PDF_EXTS = {'.pdf'}
    AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a', '.wma'}

    @staticmethod
    def detect(file_path: str) -> FileType:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext in FileDetector.IMAGE_EXTS:
            return FileType.IMAGE
        if ext in FileDetector.VIDEO_EXTS:
            return FileType.VIDEO
        if ext in FileDetector.PDF_EXTS:
            return FileType.PDF
        if ext in FileDetector.AUDIO_EXTS:
            return FileType.AUDIO
        
        return FileType.UNKNOWN
