#!/usr/bin/env python3
import sys
import os
import argparse

# Ensure project root is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.core.file_detector import FileDetector, FileType
from src.core.preset_manager import PresetManager
from src.core.image_engine import ImageEngine
from src.core.video_engine import VideoEngine
from src.core.audio_engine import AudioEngine
from src.core.pdf_engine import PdfEngine

def get_output_path(input_path, preset_data):
    input_dir = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    # Determine new extension if format change
    if preset_data.get("action") == "convert" and "format" in preset_data:
        new_ext = "." + preset_data["format"]
    else:
        new_ext = ext
        
    output_path = os.path.join(input_dir, f"{name}_converted{new_ext}")
    
    # Handle duplicates
    counter = 1
    base_output_path = output_path
    while os.path.exists(output_path):
        name_no_ext, ext_part = os.path.splitext(base_output_path)
        output_path = f"{name_no_ext}({counter}){ext_part}"
        counter += 1
        
    return output_path

def main():
    parser = argparse.ArgumentParser(description="File Converter CLI")
    parser.add_argument("files", nargs="*", help="Files to convert")
    parser.add_argument("--preset", type=str, help="Preset name to use (e.g. 'To PNG')")
    parser.add_argument("--list-presets", nargs="?", const="ALL", help="List available presets. Optionally provide a file path to filter by type.")
    parser.add_argument("--install-integration", action="store_true", help="Install context menu scripts for Nautilus/Nemo")

    args = parser.parse_args()
    
    # Handle Integration Installation
    if args.install_integration:
        from src.scripts.generate_nautilus_scripts import main as install_scripts
        print("Installing context menu integration...")
        try:
             # We need to make sure the generator uses THIS executable if frozen
            if getattr(sys, 'frozen', False):
                # When frozen, we want the scripts to point to this executable
                os.environ["FILECONVERTER_EXEC_PATH"] = sys.executable
            
            install_scripts()
            print("Integration installed successfully.")
        except Exception as e:
            print(f"Failed to install integration: {e}")
        return

    # Handle List Presets
    if args.list_presets:
        PresetManager.load_presets()
        
        filter_type = None
        if args.list_presets != "ALL" and os.path.isfile(args.list_presets):
             filter_type = FileDetector.detect(args.list_presets)
             
        if filter_type:
            presets = PresetManager.get_presets(filter_type)
            # Print just the names for easy parsing by shell scripts
            for name in presets:
                print(name)
        else:
            print("Available Presets:")
            for type_key, presets in PresetManager._presets.items():
                print(f"\n{type_key}:")
                for name in presets:
                    print(f"  - {name}")
        return

    if not args.files:
        parser.print_help()
        return

    for file_path in args.files:
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}")
            continue
            
        print(f"Processing: {file_path}")
        
        file_type = FileDetector.detect(file_path)
        if file_type == FileType.UNKNOWN:
            print(f"  Error: Unknown file type for {file_path}")
            continue
            
        presets = PresetManager.get_presets(file_type)
        preset_name = args.preset
        
        if not preset_name:
            if not presets:
                print("  Error: No presets available for this file type")
                continue
            # Default to first available
            preset_name = list(presets.keys())[0]
            print(f"  Using default preset: {preset_name}")
            
        preset_data = presets.get(preset_name)
        if not preset_data:
            print(f"  Error: Preset '{preset_name}' not found for type {file_type.name}")
            continue
            
        output_path = get_output_path(file_path, preset_data)
        print(f"  Output: {output_path}")
        
        success = False
        error_msg = ""
        
        # Holder for process (not strictly needed for CLI but Engine expects it)
        process_holder = [None]
        
        if file_type == FileType.IMAGE:
            success = ImageEngine.convert(file_path, output_path, preset_data, process_holder)
        elif file_type == FileType.VIDEO:
             # Basic progress callback
            def progress_cb(p):
                print(f"  Progress: {p}%", end='\r', flush=True)
            success = VideoEngine.convert(file_path, output_path, preset_data, process_holder, progress_cb)
            print() # Newline after progress
        elif file_type == FileType.AUDIO:
             # Basic progress callback
            def progress_cb(p):
                print(f"  Progress: {p}%", end='\r', flush=True)
            success = AudioEngine.convert(file_path, output_path, preset_data, process_holder, progress_cb)
            print() # Newline after progress
        elif file_type == FileType.PDF:
            if preset_data.get("action") == "compress":
                 success = PdfEngine.compress(file_path, output_path, preset_data, process_holder)
            else:
                 error_msg = "Action not supported for PDF"
        else:
            error_msg = "Engine not implemented"
            
        if success:
            print(f"  Success!")
        else:
            print(f"  Failed! {error_msg}")

if __name__ == "__main__":
    main()
