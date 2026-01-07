import os
from enum import Enum, auto

class FileType(Enum):
    IMAGE = auto()
    VIDEO = auto()
    PDF = auto()
    UNKNOWN = auto()

class FileDetector:
    IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
    VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    PDF_EXTS = {'.pdf'}

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
        
        return FileType.UNKNOWN
