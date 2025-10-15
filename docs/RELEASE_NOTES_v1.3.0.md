# PhotoSift v1.3.0 Release Notes

**Release Date**: October 14, 2025

## 🎉 What's New in v1.3.0

### 🌍 Unicode Path Support (Critical Fix)

**The Problem**: Users with Chinese, Japanese, Korean, or other non-English characters in their folder paths experienced a critical bug where ALL images were incorrectly marked as 100% duplicates, even when they were completely different.

**The Solution**: We completely rewrote the image loading system to properly handle Unicode file paths. PhotoSift now works seamlessly with folder and file names in ANY language!

**Who Benefits**:
- International users with native language folder names
- Anyone with special characters in file paths (accents, symbols, etc.)
- Users who organize photos with non-English naming conventions

### 🎚️ Adjustable Similarity Threshold

Take control of duplicate detection with our new **Similarity Threshold Slider** (80%-99%):

- **98-99%**: Find only identical images (pixel-perfect matches)
- **95-97%**: Near duplicates (default - recommended for most users)
- **90-94%**: Similar images (different angles, crops, edits)
- **80-89%**: Loosely related images (experimental)

**Benefits**:
- Fine-tune detection sensitivity for your specific needs
- **Fast re-grouping**: Change threshold and see results instantly (10-20x faster than re-scanning)
- Quality guide helps you choose the right threshold
- Real-time percentage display

### ⚡ Improved Scanning Workflow

**Start Scan Button**: We separated folder selection from scanning for better control:

1. **Select Folder** → See image count
2. **Adjust Threshold** → Set your preferred sensitivity
3. **Start Scan** → Begin analysis when ready

**Auto-Select Results**: After scanning or re-grouping, all duplicate groups are automatically selected and displayed - no more manual clicking to see results!

## 🐛 Bug Fixes

### Critical
- **Fixed Unicode path handling**: Images in folders with Chinese/Japanese/Korean characters now process correctly
- **Resolved false duplicate detection**: 100% similarity on different images is completely fixed

### Minor
- Improved error handling for corrupted image files
- Better memory management during large batch operations

## 🚀 Performance Improvements

- **10-20x faster re-grouping**: Change threshold without re-processing images
- **Optimized image loading**: PIL-based loading with LANCZOS resampling for quality
- **Efficient caching**: Embeddings stored in memory for instant threshold adjustments

## 📊 Technical Details

### Changed
- Image loading now uses PIL (Pillow) instead of OpenCV for Unicode support
- LANCZOS resampling for high-quality image resizing
- Improved embedding extraction workflow

### Maintained
- All 33 regression tests pass ✅
- Backward compatible with previous versions
- No new dependencies required
- All existing features work exactly as before

## 📥 Installation

### New Users
Download and run the installer:
```
PhotoSift-1.3.0-Setup.exe
```

### Upgrading from v1.2.0
Simply run the new installer - it will automatically upgrade your installation while preserving:
- Your settings
- Trash folders
- Previous classifications

### Important Note for Upgrading
If you previously had issues with folders containing Unicode characters:
1. After upgrading, re-scan those folders
2. You'll now see accurate duplicate detection
3. Previous false positives will be resolved

## 📚 Documentation

New documentation added in this release:
- `CHANGELOG.md` - Complete version history
- `UNICODE_PATH_FIX.md` - Detailed technical explanation of the Unicode fix
- `THRESHOLD_ENHANCEMENT.md` - Guide to using the threshold feature
- `START_SCAN_BUTTON_ENHANCEMENT.md` - Workflow improvements documentation
- `AUTO_SELECT_GROUPS_FEATURE.md` - Auto-select implementation details

## 🧪 Testing

This release includes comprehensive testing:
- ✅ 33 regression tests (all passing)
- ✅ Unicode path testing with Chinese characters
- ✅ Similarity threshold validation
- ✅ Memory leak testing
- ✅ Large dataset processing (1000+ images)

## 🔄 Upgrade Path

**From v1.2.0 → v1.3.0**: Direct upgrade (recommended)
**From v1.1.0 → v1.3.0**: Direct upgrade (tested)
**From v1.0.0 → v1.3.0**: Direct upgrade (tested)

## 🙏 Acknowledgments

Special thanks to users who reported the Unicode path issue and provided test cases with Chinese folder names. This feedback was instrumental in identifying and resolving this critical bug.

## 🐛 Known Issues

None identified in this release. If you encounter any issues, please report them on our GitHub issues page.

## 📞 Support

- GitHub Issues: https://github.com/peterchei/PhotoSift/issues
- Documentation: See README.md and feature documentation files
- Email: [Your support email]

## 📅 What's Next?

We're already planning v1.4.0 with:
- Video file support
- Batch export functionality
- Custom classification categories
- Cloud storage integration

---

**Download**: [PhotoSift v1.3.0 Release](https://github.com/peterchei/PhotoSift/releases/tag/v1.3.0)

**Full Changelog**: [v1.2.0...v1.3.0](https://github.com/peterchei/PhotoSift/compare/v1.2.0...v1.3.0)
