#!/bin/bash
set -e

# Ensure we are in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "Running build_linux.sh to ensure latest binary..."
./build_linux.sh

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

# Copy maintainer scripts
echo "Copying maintainer scripts..."
if [ -f "src/resources/postinst" ]; then
    cp "src/resources/postinst" "$BUILD_DIR/DEBIAN/postinst"
    chmod 755 "$BUILD_DIR/DEBIAN/postinst"
fi
if [ -f "src/resources/prerm" ]; then
    cp "src/resources/prerm" "$BUILD_DIR/DEBIAN/prerm"
    chmod 755 "$BUILD_DIR/DEBIAN/prerm"
fi

# Extract version and architecture from control file
VERSION=$(grep "Version:" "src/resources/control" | awk '{print $2}')
ARCH=$(grep "Architecture:" "src/resources/control" | awk '{print $2}')
DEB_NAME="fileconverter_${VERSION}_${ARCH}.deb"

# Build package
echo "Building .deb..."
dpkg-deb --build "$BUILD_DIR" "$DEB_NAME"

echo "Package created: $DEB_NAME"
echo "To install: sudo dpkg -i $DEB_NAME"
