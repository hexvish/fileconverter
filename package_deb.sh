#!/bin/bash
set -e

# Ensure we are in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# verify dist/FileConverter exists
if [ ! -f "dist/FileConverter" ]; then
    echo "Error: dist/FileConverter not found. Running build_linux.sh..."
    ./build_linux.sh
fi

echo "Creating Debian Package..."

# Prepare directories
BUILD_DIR="build/deb"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/local/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"

# Copy binary
echo "Copying binary..."
cp "dist/FileConverter" "$BUILD_DIR/usr/local/bin/fileconverter"
chmod 755 "$BUILD_DIR/usr/local/bin/fileconverter"

# Copy and update desktop file
echo "Configuring desktop entry..."
# We use sed to replace the Exec path with the installed path
sed 's|Exec=.*|Exec=/usr/local/bin/fileconverter %F|' fileconverter.desktop > "$BUILD_DIR/usr/share/applications/fileconverter.desktop"
# Also ensure Icon is generic or instal an icon (Using utilities-terminal for now as per original)

# Copy control file
echo "Copying control file..."
cp "src/resources/control" "$BUILD_DIR/DEBIAN/control"

# Build package
echo "Building .deb..."
dpkg-deb --build "$BUILD_DIR" "fileconverter_1.0.0_amd64.deb"

echo "Package created: fileconverter_1.0.0_amd64.deb"
echo "To install: sudo dpkg -i fileconverter_1.0.0_amd64.deb"
