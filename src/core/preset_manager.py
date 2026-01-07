import json
import os
from src.core.file_detector import FileType

class PresetManager:
    _presets = {}

    @classmethod
    def load_presets(cls):
        # Locate presets.json relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to src, then into resources
        json_path = os.path.join(os.path.dirname(current_dir), 'resources', 'presets.json')
        
        try:
            with open(json_path, 'r') as f:
                cls._presets = json.load(f)
        except FileNotFoundError:
            print(f"Error: presets.json not found at {json_path}")
            cls._presets = {}
        except json.JSONDecodeError:
             print(f"Error: presets.json is invalid")
             cls._presets = {}

    @classmethod
    def get_presets(cls, file_type: FileType) -> dict:
        if not cls._presets:
            cls.load_presets()
            
        type_str = file_type.name  # IMAGE, VIDEO, PDF
        return cls._presets.get(type_str, {})
