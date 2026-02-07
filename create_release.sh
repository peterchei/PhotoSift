#!/bin/bash
set -e

# Get version from user
if [ -z "$1" ]; then
    read -p "Enter release version (e.g., 1.0.0): " VERSION
else
    VERSION=$1
fi

# Create and push git tag
echo "Tagging version v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin "v$VERSION"

# Run the build script
echo "Running build.sh..."
./build.sh

# Calculate checksums
echo "Calculating checksums..."
echo "SHA-256 Checksums:" > checksums.txt
if [ -f "dist/PhotoSift" ]; then
    sha256sum "dist/PhotoSift" >> checksums.txt
fi

echo ""
echo "Release v$VERSION has been tagged and built."
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/peterchei/PhotoSift/releases/new"
echo "2. Choose tag v$VERSION"
echo "3. Upload files from:"
echo "   - dist/PhotoSift"
echo "4. Copy checksums from checksums.txt"
echo ""
if [ -f "checksums.txt" ]; then
    cat checksums.txt
fi
