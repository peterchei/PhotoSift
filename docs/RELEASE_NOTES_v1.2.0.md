# PhotoSift v1.2.0 Release Notes

**Release Date:** October 12, 2025

## 🎉 What's New in v1.2.0

### Enhanced User Interface
- **Dynamic Button Text**: Select All button now intelligently displays "Select All" or "Unselect All" based on current selection state
- **Comprehensive Tooltips**: Added helpful tooltips to Select All and Clean buttons in both DuplicateImageIdentifierGUI and ImageClassifierGUI
- **Improved Image Viewer**: Enhanced image information display with comprehensive EXIF metadata including:
  - Full file path with copy-to-clipboard functionality (Ctrl+C)
  - Camera make and model
  - Date taken
  - Exposure settings (f-stop, shutter speed, ISO, focal length)
  - GPS location indicator
  - File size, dimensions, format, and color mode

### Duplicate Image Identifier Improvements
- **Group-Based Paging**: Pagination now works by duplicate groups (10 groups per page) instead of individual images, ensuring all duplicate images from the same group stay together on the same page
- **Smart Selection**: Select All button intelligently keeps the first image in each group unchecked (treating it as the original)
- **Better State Management**: Select All button text now properly resets across all user actions:
  - Page navigation (Next/Previous)
  - After cleanup operations
  - Manual checkbox changes
  - Initial display

### Quality of Life Enhancements
- **Double-Click to Close**: Image viewer windows now close when double-clicking the image
- **Real-time Updates**: Duplication count label now updates immediately after cleanup operations
- **Consistent UI**: Applied modern dark theme styling consistently across all components

## 🐛 Bug Fixes
- Fixed duplication count label not updating after cleaning images
- Fixed Select All button text not resetting when navigating between pages
- Fixed Select All button text not resetting after cleanup operations
- Improved state synchronization between UI elements

## 🔧 Technical Improvements
- Enhanced EXIF data extraction with better error handling
- Improved performance with proper event binding/unbinding patterns
- Better state management flags to prevent recursive calls
- Optimized LRU cache for thumbnail images

## 📦 Installation

### Windows Installer
Download and run `PhotoSift_Setup_v1.2.0.exe`

### Standalone Executable
Download `PhotoSift_v1.2.0.exe` - no installation required

### From Source
```bash
git clone https://github.com/peterchei/PhotoSift.git
cd PhotoSift
git checkout v1.2.0
pip install -e .
python src/launchPhotoSiftApp.py
```

## 🔄 Upgrading from v1.1.0
Simply install the new version. All your settings and preferences will be preserved.

## 📝 Known Issues
- None reported yet

## 🙏 Acknowledgments
Thank you to all users who provided feedback and suggestions for these improvements!

## 📄 License
MIT License - See LICENSE file for details

---

**Full Changelog**: [v1.1.0...v1.2.0](https://github.com/peterchei/PhotoSift/compare/v1.1.0...v1.2.0)

*For more information, visit the [PhotoSift GitHub repository](https://github.com/peterchei/PhotoSift)*
