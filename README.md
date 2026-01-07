# FileConverter

FileConverter is a powerful, desktop-integrated file conversion utility.
It currently targets Linux, with Windows support planned.


![FileConverter GUI]

## Features

-   **Image Conversion**: Convert between `JPG`, `PNG`, `WEBP`, `PDF`. Resize and optimize for Web/Email.
-   **Video Conversion**: Convert `MP4`, `AVI`, `WEBM`, `MKV`. Standard quality presets (1080p, 720p).
-   **Audio Support**:
    -   Convert Audio: `MP3`, `WAV`, `OGG`, `FLAC`, `AAC`, etc.
    -   **Extract Audio**: Extract audio tracks from video files directly to `MP3` or `WAV`.
-   **PDF Tools**: Compress PDFs for Screen/Web or Ebook/Printing quality.
-   **System Integration**:
    -   **Context Menu**: Right-click files in Nautilus (GNOME) or Nemo (Linux Mint) to convert instantly.
    -   **Open With**: Open files directly into the FileConverter GUI.

## Requirements

-   **Python 3.10+**
-   **System Dependencies**:
    ```bash
    sudo apt install ffmpeg imagemagick ghostscript
    ```

## Installation

1.  **Clone and Setup**:
    ```bash
    git clone <repo-url>
    cd fileconverter
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Install Desktop Entry** (for "Open With"):
    ```bash
    cp fileconverter.desktop ~/.local/share/applications/
    update-desktop-database ~/.local/share/applications/
    ```

3.  **Install Context Menu Scripts** (Nautilus/Nemo):
    ```bash
    python src/scripts/generate_nautilus_scripts.py
    ```
    *Restart your file manager (`nautilus -q` or `nemo -q`) to see the changes.*

## Usage

### GUI
Run the application:
```bash
python src/main.py
```
Or use "Open With... FileConverter" on any supported file.

### Context Menu
1.  Right-click files in your file manager.
2.  Navigate to **Scripts > File Converter**.
3.  Select a preset (e.g., `Image > To PNG` or `Video > Extract Audio (MP3)`).
4.  A progress window will appear and process your files.

### Command Line (CLI)
Headless conversion from the terminal:
```bash
# List available presets
python src/cli.py --list-presets

# Convert files
python src/cli.py input.jpg --preset "To PNG"
python src/cli.py video.mp4 --preset "Extract Audio (MP3)"
```

### Quick Convert (GUI Launcher)
Launch the GUI directly into conversion mode:
```bash
python src/main.py --quick-convert "To JPG" file1.png file2.png
```

## Structure
-   `src/main.py`: Entry point for GUI.
-   `src/cli.py`: Entry point for CLI.
-   `src/core/`: Engines (FFmpeg, ImageMagick, Ghostscript) and logic.
-   `src/resources/presets.json`: Configurable conversion presets.
-   `src/scripts/`: Integration scripts.
