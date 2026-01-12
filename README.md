# FileConverter

FileConverter is a powerful, desktop-integrated file conversion utility.
It currently targets Linux, with Windows support planned.

## Features

-   **Image Conversion**:
    -   Convert between `JPG`, `PNG`, `WEBP`, `PDF`.
    -   **Custom Resolution**: Set specific Width/Height and Format via a GUI dialog.
-   **Video Conversion**:
    -   Convert `MP4`, `AVI`, `WEBM`, `MKV`.
    -   **Extract Audio**: Extract audio tracks directly to `MP3` or `WAV`.
    -   **Custom Resize**: Force specific dimensions (e.g., convert landscape to portrait).
-   **Audio Support**: Convert `MP3`, `WAV`, `OGG`, `FLAC`, `AAC`.
-   **Media Info Tool**: Instant popup displaying codec, resolution, bitrate, and file size details.
-   **PDF Tools**: Compress PDFs for Screen/Web or Ebook/Printing.
-   **System Integration**:
    -   **Right-Click Menu**: Seamless integration with Nautilus (GNOME) and Nemo (Linux Mint/Cinnamon).
    -   **Open With**: Open files directly into the FileConverter GUI.
    -   **Open File Location**: Right-click on completed jobs to open the output folder.

## Requirements

-   **Python 3.10+**
-   **System Dependencies**:
    ```bash
    sudo apt install ffmpeg imagemagick ghostscript
    ```

## Installation

### Method 1: Linux (Debian/Ubuntu)
Download the latest `.deb` release and install it:

```bash
sudo dpkg -i fileconverter_1.2.4_amd64.deb
```
*(Make sure to replace the version number with the file you downloaded)*

**Enable Context Menu:**
After installing, run this command once to set up the right-click menu:
```bash
fileconverter --install-integration
```
*Then restart your file manager (`nautilus -q` or `nemo -q`).*

### Method 2: Windows
Since this is primarily a Linux tool, Windows support is currently in **Beta**. You must build the executable yourself on a Windows machine:

1.  **Clone the repo** on Windows.
2.  Run `build_windows.bat` (This installs Python deps and builds the `.exe`).
3.  The executable will be in `dist\FileConverter\FileConverter.exe`.
4.  **Context Menu**: Run `python src/scripts/register_windows.py` (as Admin) to add the "Convert with FileConverter" right-click option.
5.  Currently windows is not working as expected.

### Method 3: From Source (Developers)

## Usage

### 1. Context Menu (Right-Click)
The primary way to use FileConverter is via the file manager:
1.  **Right-click** files in Nautilus or Nemo.
2.  Navigate to **Scripts > File Converter**.
3.  Select an option:
    -   **Presets**: e.g., `Image > To PNG`, `Video > Extract Audio`.
    -   **Custom...**: Define custom Width, Height, and Format.
    -   **00_Media Info**: View file metadata.

### 2. Desktop App
Search for **FileConverter** in your system menu to launch the standalone GUI. Custom presets and batch jobs can be managed here.

### 3. Command Line (CLI)
```bash
# List available presets
fileconverter --list-presets

# Quick Convert (Dialog Mode)
fileconverter --quick-convert "To PNG" image.jpg

# Media Info
fileconverter --media-info video.mp4
```

## Development

### Running from Source
1.  **Clone and Setup**:
    ```bash
    git clone <repo-url>
    cd fileconverter
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Run**:
    ```bash
    python src/main.py
    ```

### Project Structure
-   `src/main.py`: GUI Entry point.
-   `src/cli.py`: CLI Entry point.
-   `src/core/`: Engines (FFmpeg, ImageMagick) and business logic.
-   `src/resources/`: Assets and Presets config.
-   `src/scripts/`: Context menu integration scripts.
