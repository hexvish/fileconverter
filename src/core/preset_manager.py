import json
import os
import sys
from src.core.file_detector import FileType

class PresetManager:
    _presets = None # Changed to None to indicate not loaded yet

    @staticmethod
    def _load_presets_internal():
        if PresetManager._presets is not None:
            return

        # Determine path to specific presets.json
        # Handle PyInstaller frozen state
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
             # resources folder is added to root of bundle in build script
            base_path = os.path.join(sys._MEIPASS, "src", "resources")
            # If that fails, check root resources (depends on spec)
            if not os.path.exists(base_path):
                 base_path = os.path.join(sys._MEIPASS, "resources")
        else:
            # Development path
            # Go up three levels from current file (src/core/preset_manager.py) to project root, then into src/resources
            base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "resources")

        json_path = os.path.join(base_path, "presets.json")
        
        if not os.path.exists(json_path):
            # Fallback for some dev environments (e.g., running from src/core)
            json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/presets.json"))

        if not os.path.exists(json_path):
            print(f"Error: presets.json not found at {json_path}")
            PresetManager._presets = {}
            return

        try:
            with open(json_path, 'r') as f:
                PresetManager._presets = json.load(f)
        except FileNotFoundError: # This should ideally be caught by the os.path.exists check, but kept for robustness
            print(f"Error: presets.json not found at {json_path}")
            PresetManager._presets = {}
        except json.JSONDecodeError:
             print(f"Error: presets.json is invalid")
             PresetManager._presets = {}

    @classmethod
    def load_presets(cls):
        cls._load_presets_internal()

    @classmethod
    def get_presets(cls, file_type: FileType) -> dict:
        if cls._presets is None: # Check if presets have been loaded
            cls.load_presets()
            
        type_str = file_type.name  # IMAGE, VIDEO, PDF
        return cls._presets.get(type_str, {})
