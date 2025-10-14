# PhotoSift v1.3.0 Release - Quick Reference

## Version Information
- **Version**: 1.3.0
- **Release Date**: October 14, 2025
- **Previous Version**: 1.2.0
- **Release Type**: Major feature release with critical bug fix

## Key Changes Summary

### 🐛 Critical Bug Fix
**Unicode Path Support**: Fixed issue where folders with Chinese/Japanese/Korean characters caused false 100% duplicate detection.

### ✨ New Features
1. **Adjustable Similarity Threshold** (80%-99%)
2. **Start Scan Button** (separated from folder selection)
3. **Auto-Select Groups** (immediate result display)

### 📈 Performance
- 10-20x faster threshold re-grouping
- Improved image loading with Unicode support

## Files Updated

### Version Files
- ✅ `setup.py` → v1.3.0
- ✅ `version_info.txt` → v1.3.0 (filevers and FileVersion)
- ✅ `create_store_assets.py` → v1.3.0
- ✅ `create_store_package.bat` → v1.3.0.0

### Documentation
- ✅ `CHANGELOG.md` (NEW)
- ✅ `RELEASE_NOTES_v1.3.0.md` (NEW)
- ✅ `RELEASE_CHECKLIST_v1.3.0.md` (NEW)
- ✅ `UNICODE_PATH_FIX.md` (already created)
- ✅ `THRESHOLD_ENHANCEMENT.md` (already created)
- ✅ `START_SCAN_BUTTON_ENHANCEMENT.md` (already created)
- ✅ `AUTO_SELECT_GROUPS_FEATURE.md` (already created)

### Code Changes
- ✅ `src/DuplicateImageIdentifier.py` - Unicode path fix

### Build Scripts
- ✅ `prepare_release.bat` (NEW) - Automated release preparation

## Testing Status

### Regression Tests
- ✅ All 33 tests passing
- ✅ test_blur_detection (11 tests)
- ✅ test_common_ui (8 tests)
- ✅ test_duplicate_detection (7 tests)
- ✅ test_image_classification (7 tests)

### Feature Testing
- ✅ Unicode path handling verified
- ✅ Threshold slider functionality tested
- ✅ Start scan button workflow validated
- ✅ Auto-select groups confirmed working

## Build Commands

### Build Executable
```batch
build.bat
```

This script will:
1. Clean previous builds (dist, build, __pycache__)
2. Create/activate virtual environment
3. Install dependencies
4. Build executable with PyInstaller
5. Create installer with Inno Setup (if available)

### Build Microsoft Store Package (Optional)
```batch
create_store_package.bat
```

This script will:
1. Run build.bat to create executable
2. Generate store assets (logos, icons)
3. Create AppxManifest.xml with v1.3.0.0
4. Prepare store_package directory for MSIX creation

### Run Tests
```batch
cd tests
python run_all_tests.py
cd ..
```

## Git Commands

### Commit Changes
```bash
git add .
git commit -m "Release v1.3.0: Unicode support, threshold control, and UX improvements

Major changes:
- Fixed critical Unicode path bug affecting international users
- Added adjustable similarity threshold (80%-99%) for duplicate detection
- Added Start Scan button for better workflow control
- Added auto-select groups for immediate result display
- Comprehensive documentation and testing

Full changelog in CHANGELOG.md"
```

### Create and Push Tag
```bash
# Create annotated tag
git tag -a v1.3.0 -m "PhotoSift v1.3.0

Major Release: Unicode Support and Enhanced User Control

Key Features:
- Unicode path support for international users
- Adjustable similarity threshold with fast re-grouping
- Improved scanning workflow with Start Scan button
- Auto-select groups for instant result display

Bug Fixes:
- Fixed critical Unicode path handling issue
- Resolved false duplicate detection for non-English paths

See RELEASE_NOTES_v1.3.0.md for detailed release notes."

# Push commits and tags
git push origin master
git push origin v1.3.0
```

## GitHub Release

### Create Release
1. Go to: https://github.com/peterchei/PhotoSift/releases/new
2. Select tag: **v1.3.0**
3. Release title: **PhotoSift v1.3.0 - Unicode Support & Enhanced Control**
4. Description: Copy from `RELEASE_NOTES_v1.3.0.md`
5. Upload assets:
   - `dist/PhotoSift.exe`
6. Click "Publish release"

## Post-Release Verification

### Checklist
- [ ] GitHub release is visible
- [ ] Download link works
- [ ] Executable runs on Windows 10/11
- [ ] Unicode paths work correctly
- [ ] All three tools function properly
- [ ] Documentation links are correct

### Test Cases
1. **Unicode Test**: Scan `E:\Peter's Photo\22-03-2002 華山派聚會`
   - Expected: Realistic similarity scores (not all 100%)

2. **Threshold Test**: Adjust from 95% to 80%
   - Expected: Fast re-grouping (<5 seconds for 100 images)

3. **Workflow Test**: Select folder → See count → Start scan
   - Expected: Smooth workflow, auto-display results

## Troubleshooting

### Build Issues
```batch
# Clean and rebuild
rmdir /s /q dist
rmdir /s /q build
del PhotoSift.spec
build.bat
```

### Test Failures
```batch
# Run specific test
cd tests
python -m unittest test_duplicate_detection
cd ..
```

### Version Mismatch
Check these files have v1.3.0:
- `setup.py` → line 5
- `version_info.txt` → lines 9, 10, 34, 38

## Support Resources

- **Issues**: https://github.com/peterchei/PhotoSift/issues
- **Discussions**: https://github.com/peterchei/PhotoSift/discussions
- **Documentation**: See README.md and feature docs

## Next Version Planning

Ideas for v1.4.0:
- Video file support
- Batch export functionality
- Custom classification categories
- Cloud storage integration
- Multi-language UI
- Advanced filtering options

---

**Quick Start**: Run `prepare_release.bat` to automate most of the release process!
