#!/bin/bash
# PhotoSift v1.6.0 Release Preparation Script
# This script automates the release preparation process for Linux

set -e

echo "================================================================"
echo "PhotoSift v1.6.0 Release Preparation (Linux)"
echo "================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "ERROR: setup.py not found. Please run this script from the PhotoSift root directory."
    exit 1
fi

echo "[1/6] Running regression tests..."
echo "----------------------------------------------------------------"
source build_env_linux/bin/activate
python3 tests/run_all_tests.py
echo ""
echo "✓ All tests passed!"
echo ""

echo "[2/6] Checking Python syntax..."
echo "----------------------------------------------------------------"
FILES=("src/DuplicateImageIdentifier.py" "src/DuplicateImageIdentifierGUI.py" "src/ImageClassification.py" "src/ImageClassifierGUI.py" "src/BlurryImageDetection.py" "src/BlurryImageDetectionGUI.py" "src/CommonUI.py" "src/launchPhotoSiftApp.py")

for file in "${FILES[@]}"; do
    python3 -m py_compile "$file"
    echo "✓ $file"
done
echo ""
echo "✓ All Python files have valid syntax!"
echo ""

echo "[3/6] Cleaning previous builds..."
echo "----------------------------------------------------------------"
rm -rf dist build
echo "✓ Removed build artifacts"
echo ""

echo "[4/6] Building executable..."
echo "----------------------------------------------------------------"
./build.sh
echo ""
echo "✓ Build completed successfully!"
echo ""

echo "[5/6] Verifying build output..."
echo "----------------------------------------------------------------"
if [ ! -f "dist/PhotoSift" ]; then
    echo "ERROR: PhotoSift not found in dist directory!"
    exit 1
fi

# Check file size (should be > 100MB due to PyTorch and models)
SIZE=$(stat -c%s "dist/PhotoSift")
if [ "$SIZE" -lt 100000000 ]; then
    echo "WARNING: PhotoSift seems too small ($SIZE bytes)"
    echo "This might indicate a packaging issue."
fi

echo "✓ PhotoSift found in dist directory"
echo "  Size: $SIZE bytes"
echo ""

echo "[6/6] Checking version consistency..."
echo "----------------------------------------------------------------"
grep -q "version=\"1.6.0\"" setup.py
echo "✓ setup.py: version 1.6.0"

grep -q "filevers=(1, 6, 0, 0)" version_info.txt
echo "✓ version_info.txt: filevers 1.6.0"

grep -q "FileVersion\", u\"1.6.0\"" version_info.txt
echo "✓ version_info.txt: FileVersion 1.6.0"

echo ""
echo "================================================================"
echo "Release Preparation Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. Test the executable: dist/PhotoSift"
echo "  2. Verify all features work correctly"
echo "  3. Review RELEASE_CHECKLIST_v1.3.0.md (if applicable)"
echo "  4. Commit changes and create git tag"
echo "  5. Push to GitHub and create release"
echo ""
echo "Git commands:"
echo "  git add ."
echo "  git commit -m \"Release v1.6.0\""
echo "  git tag -a v1.6.0 -m \"PhotoSift v1.6.0 Release\""
echo "  git push upstream master"
echo "  git push upstream v1.6.0"
echo "================================================================"
