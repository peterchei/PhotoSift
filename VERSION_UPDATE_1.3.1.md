# Version Update to 1.3.1 - Release Preparation

## Overview
Updated all version numbers from **1.3.0** to **1.3.1** across build scripts and configuration files in preparation for the next release.

## Changes Made

### ✅ Files Updated (5 files)

#### 1. **setup.py**
- **Line 5**: `version="1.3.0"` → `version="1.3.1"`

#### 2. **version_info.txt**
- **Line 9**: `filevers=(1, 3, 0, 0)` → `filevers=(1, 3, 1, 0)`
- **Line 10**: `prodvers=(1, 3, 0, 0)` → `prodvers=(1, 3, 1, 0)`
- **Line 34**: `StringStruct(u'FileVersion', u'1.3.0')` → `StringStruct(u'FileVersion', u'1.3.1')`
- **Line 38**: `StringStruct(u'ProductVersion', u'1.3.0')` → `StringStruct(u'ProductVersion', u'1.3.1')`

#### 3. **pyproject.toml**
- **Line 7**: `version = "1.2.0"` → `version = "1.3.1"`
  - Note: This was outdated at 1.2.0, now updated to 1.3.1

#### 4. **create_store_package.bat**
- **Line 26**: `Version="1.3.0.0"` → `Version="1.3.1.0"`

#### 5. **create_store_assets.py**
- **Line 25**: Display message updated from v1.3.0 to v1.3.1

## Version Update Summary

### Build Configuration
- **Python Package Version**: 1.3.1 (setup.py, pyproject.toml)
- **Windows Executable Version**: 1.3.1.0 (version_info.txt)
- **Microsoft Store Package Version**: 1.3.1.0 (create_store_package.bat)

### What's New in 1.3.1

Based on recent changes, version 1.3.1 includes:

1. **GUI Consistency Improvements**
   - Standardized window titles across all three GUIs (all prefixed with "PhotoSift")
   - Unified button styling using ModernButton factory
   - Consistent button colors (Blue for actions, Red for destructive operations)

2. **UI Refinements**
   - Reduced vertical spacing in DuplicateImageIdentifier sidebar (8px vs 15px)
   - Improved layout density and visual hierarchy

3. **Launcher Improvements**
   - Selection window now appears in Windows taskbar
   - Added app icon to selection window title bar
   - Better window visibility and accessibility

4. **MS Store Crash Fixes** (from 1.3.0)
   - PyInstaller path configuration for frozen executables
   - Comprehensive error handling with user-friendly messages
   - Thread-safe model loading with timeouts
   - Enhanced logging for debugging

## Next Steps - Release Process

Following the ReleaseSteps.md guide:

### 1. Commit Version Updates ✅ (Ready)
```bash
git add setup.py version_info.txt pyproject.toml create_store_package.bat create_store_assets.py
git commit -m "Bump version to 1.3.1"
git push
```

### 2. Build Desktop Packages
```bash
.\build.bat
```
Expected output:
- `dist/PhotoSift.exe` - Standalone executable
- `Output/PhotoSift_Setup.exe` - Windows installer

### 3. Build Microsoft Store Package
```bash
# Method 1: Step by step
python create_store_assets.py
.\create_store_package.bat
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift_v1.3.1.msix

# Method 2: One command
python create_store_assets.py && .\create_store_package.bat && & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift_v1.3.1.msix
```

### 4. Test Builds
- [ ] Test standalone executable: `.\dist\PhotoSift.exe`
- [ ] Test installer: Install and run from Start Menu
- [ ] Test MSIX package: Install locally and verify

### 5. Create GitHub Release
- [ ] Tag version: `git tag v1.3.1`
- [ ] Push tag: `git push origin v1.3.1`
- [ ] Create GitHub release with binaries
- [ ] Add release notes

### 6. Submit to Microsoft Store
- [ ] Upload PhotoSift_v1.3.1.msix to Partner Center
- [ ] Update store listing if needed
- [ ] Submit for certification

## Verification Commands

### Check Version Numbers
```bash
# Python package version
python -c "import setup; print(setup.version)"

# Version info file
type version_info.txt | findstr "filevers\|FileVersion"

# Store package version
type create_store_package.bat | findstr "Version="

# pyproject.toml version
type pyproject.toml | findstr "version"
```

### Verify All Show 1.3.1
All version references should now show **1.3.1** (or **1.3.1.0** for Windows/Store formats).

## Changelog Summary for 1.3.1

**GUI & UX Improvements:**
- Standardized window titles with "PhotoSift" prefix
- Unified button colors and styling across all three applications
- Improved sidebar spacing and layout density
- Enhanced launcher window visibility in taskbar

**Technical:**
- All build scripts and configuration updated to version 1.3.1
- Consistent versioning across all deployment targets

**Previous (1.3.0) - Already Released:**
- Unicode path support for international filenames
- MS Store crash fixes with comprehensive error handling
- PyInstaller compatibility improvements

---

**Status**: ✅ Version numbers updated, ready to build and release  
**Version**: 1.3.1  
**Date**: October 15, 2025  
**Files Modified**: 5 (setup.py, version_info.txt, pyproject.toml, create_store_package.bat, create_store_assets.py)
