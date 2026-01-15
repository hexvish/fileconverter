@echo off
echo Building Application...
call build_windows.bat

if %ERRORLEVEL% NEQ 0 (
    echo "Application build failed!"
    exit /b %ERRORLEVEL%
)

echo.
echo Building Standalone Installer...

REM Create a temporary spec for the installer to bundle the app
REM We need to bundle:
REM 1. dist/FileConverter folder -> placed at root of bundle (accessed via sys._MEIPASS/FileConverter)
REM 2. src/resources/presets.json -> placed at root of bundle (accessed via sys._MEIPASS/presets.json)

REM Note: data format is "source;dest"
pyinstaller --noconfirm --onefile --console --name "FileConverterInstaller" ^
    --add-data "dist/FileConverter;FileConverter" ^
    --add-data "src/resources/presets.json;." ^
    src/scripts/install.py

if %ERRORLEVEL% NEQ 0 (
    echo "Installer build failed!"
    exit /b %ERRORLEVEL%
)

echo.
echo ==========================================
echo Installer created successfully!
echo Location: dist\FileConverterInstaller.exe
echo ==========================================
