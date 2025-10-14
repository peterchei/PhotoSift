# Changelog

All notable changes to PhotoSift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-10-14

### Fixed
- **Critical Unicode Path Bug**: Fixed issue where images in folders with Chinese characters (or other Unicode characters) were incorrectly marked as 100% duplicates
  - Root cause: OpenCV's `cv2.imread()` cannot handle Unicode paths on Windows
  - Solution: Replaced OpenCV with PIL (Pillow) for image loading in `DuplicateImageIdentifier.py`
  - Impact: All international users can now use PhotoSift with native language folder/file names
  - Details documented in `UNICODE_PATH_FIX.md`

### Enhanced
- **Similarity Threshold Control**: Added adjustable similarity threshold (80%-99%) for duplicate detection
  - User-controllable slider with real-time percentage display
  - Quality guide showing what each threshold range means (Identical/Near duplicates/Similar/Loosely related)
  - Fast re-grouping with cached embeddings (10-20x speedup)
  - Details documented in `THRESHOLD_ENHANCEMENT.md`

- **Start Scan Button**: Separated folder selection from scanning operation
  - Select folder and see image count before starting scan
  - Explicit "Start Scan" button for better control
  - Improved user workflow and scanning experience
  - Details documented in `START_SCAN_BUTTON_ENHANCEMENT.md`

- **Auto-Select Groups**: Automatically select all duplicate groups after scan/re-group
  - Immediate visual feedback after operations complete
  - No manual selection needed to view results
  - Improved user experience with instant result display
  - Details documented in `AUTO_SELECT_GROUPS_FEATURE.md`

### Improved
- **Image Loading Performance**: PIL-based loading maintains high quality while supporting Unicode
- **Error Handling**: Better error messages when images fail to load
- **Code Quality**: Simplified image loading logic, removed OpenCV dependency for image I/O

### Technical
- Replaced `cv2.imread()` with `Image.open()` for Unicode-safe file path handling
- Used LANCZOS resampling for high-quality image resizing
- Maintained backward compatibility with all existing features
- All 33 regression tests pass

### Known Issues
- None identified in this release

## [1.2.0] - 2025-10-XX

### Added
- Blur Detection GUI with adjustable threshold
- Modern dark-themed UI across all tools
- Progress windows with detailed status updates
- Comprehensive test suite (33 tests)

### Enhanced
- Improved duplicate detection accuracy
- Better memory management with image caching
- Zoom controls for image inspection

## [1.1.0] - 2025-XX-XX

### Added
- Duplicate image detection using CLIP embeddings
- Similarity scoring system
- Group-based duplicate organization

## [1.0.0] - 2025-XX-XX

### Added
- Initial release
- Image classification (People vs Screenshots)
- Blur detection
- Basic GUI with modern styling
- Trash management system

---

## Release Notes

### Version 1.3.0 Highlights

This release focuses on **internationalization** and **user experience improvements**:

🌍 **Unicode Support**: PhotoSift now works seamlessly with folder and file names in any language (Chinese, Japanese, Korean, Arabic, etc.)

🎚️ **Fine-Tuned Control**: Adjust duplicate detection sensitivity with the new threshold slider

⚡ **Faster Workflow**: Separate folder selection from scanning, and auto-display results

🐛 **Bug Fixes**: Resolved critical issue affecting users with non-English folder names

### Upgrade Instructions

1. Download the latest installer from the releases page
2. Run the installer (will automatically upgrade from previous versions)
3. Your settings and trash folders will be preserved
4. Re-scan any folders that were showing false duplicates

### For International Users

If you previously experienced issues with folders containing Chinese, Japanese, Korean, or other Unicode characters:

1. The issue has been completely resolved
2. Re-scan affected folders to get accurate duplicate detection
3. All your images will now be properly analyzed

---

[1.3.0]: https://github.com/peterchei/PhotoSift/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/peterchei/PhotoSift/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/peterchei/PhotoSift/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/peterchei/PhotoSift/releases/tag/v1.0.0
