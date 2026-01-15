@echo off
SETLOCAL EnableDelayedExpansion

echo ========================================
echo FileConverter Windows Builder
echo ========================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Create Venv if missing
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate Venv
call .venv\Scripts\activate.bat

:: Install Requirements
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

:: Build
echo Building Executable...
:: --windowed: No console window
:: --noconfirm: Overwrite output
:: --clean: Clean cache
:: --add-data: Include presets.json (Syntax: source;dest)
pyinstaller --noconfirm --clean --windowed ^
    --name "FileConverter" ^
    --add-data "src/resources/presets.json;src/resources" ^
    --hidden-import "PySide6.QtXml" ^
    run.py

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo Build Successful!
    echo Executable is located at: dist\FileConverter\FileConverter.exe
    echo ========================================
) else (
    echo ========================================
    echo Build FAILED.
    echo ========================================
pause
