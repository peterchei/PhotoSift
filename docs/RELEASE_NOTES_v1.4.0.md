# PhotoSift v1.4.0 - Code Refactoring and UI Improvements

**Release Date:** October 19, 2025

## ✨ Major Features

### Shared FileOperations Class
- **Centralized File Operations**: Created a shared `FileOperations` class in `CommonUI.py` for consistent file operations across all GUI applications
- **Reduced Code Duplication**: Eliminated ~230 lines of duplicated code across the three GUI applications (ImageClassifierGUI, BlurryImageDetectionGUI, DuplicateImageIdentifierGUI)
- **Unified File Moving Logic**: All applications now use the same file moving and completion popup logic
- **Better Maintainability**: Future file operation improvements will automatically apply to all GUIs

## 🎨 UI Improvements

### Standardized Interface
- **Window Titles**: All GUI applications now have standardized window titles prefixed with "PhotoSift"
- **Button Styling**: Unified button colors and styling across all applications
  - Blue buttons for primary actions
  - Red buttons for destructive operations (like Clean/Delete)
- **Layout Consistency**: Improved sidebar spacing and visual hierarchy
- **Launcher Enhancements**: Better window visibility in taskbar with proper icon display

## 🔧 Technical Enhancements

### Code Quality
- **Refactored File Operations**: All file moving logic now uses the shared `FileOperations.move_images_to_trash()` method
- **Consistent Error Handling**: Unified exception handling and user feedback across applications
- **Improved Code Organization**: Better separation of concerns between shared utilities and GUI-specific logic
- **Regression Testing**: All existing functionality verified to work correctly after refactoring

### Build System
- **Version Management**: Updated all version numbers to 1.4.0 across build scripts and configuration files
- **Package Integrity**: All build artifacts (exe, installer, MSIX) created successfully with correct versioning

## 📦 Package Information

### File Sizes (Approximate)
- **Standalone Executable**: `PhotoSift.exe` (~614 MB)
- **Windows Installer**: `PhotoSift_Setup.exe` (~613 MB)
- **Microsoft Store Package**: `PhotoSift.msix` (~612 MB)

### System Requirements
- Windows 10 version 1903 (19H1) or later
- Windows 11 (all versions)
- 8 GB RAM recommended
- 2 GB free disk space for installation

## 🐛 Bug Fixes
- None in this release (focus on code quality and UI consistency)

## 🔄 Migration Notes
- **Backward Compatibility**: All existing features work exactly as before
- **No Data Migration**: No user data or settings need to be migrated
- **Automatic Updates**: Existing installations will continue to work normally

## 📋 Installation Instructions

### Standalone Installation
1. Download `PhotoSift.exe` from the releases page
2. Run the executable (no installation required)
3. The application will start immediately

### Full Installation (Recommended)
1. Download `PhotoSift_Setup.exe` from the releases page
2. Run the installer as administrator
3. Follow the installation wizard
4. Launch PhotoSift from the Start Menu or desktop shortcut

### Microsoft Store
1. The MSIX package is available for Microsoft Store submission
2. Will be available through Microsoft Store once certified

## 🧪 Testing
- All three GUI applications tested for file operations
- Build verification completed on Windows 11
- Package integrity verified
- Version numbers confirmed across all artifacts

## 🙏 Acknowledgments
- Thanks to all users for feedback and bug reports
- Special thanks to the open-source community for PyTorch, Transformers, and other dependencies

---

**Checksums:**
- PhotoSift.exe: SHA256 verification available in release assets
- PhotoSift_Setup.exe: SHA256 verification available in release assets
- PhotoSift.msix: SHA256 verification available in release assets

**Previous Version:** [v1.3.1](https://github.com/peterchei/PhotoSift/releases/tag/v1.3.1) | [Changelog](https://github.com/peterchei/PhotoSift/blob/master/docs/CHANGELOG.md)