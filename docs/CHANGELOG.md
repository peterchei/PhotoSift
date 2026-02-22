# Changelog

All notable changes to PhotoSift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-02-22

### Added
- **Low Resolution Detector** — new fifth tool in the PhotoSift launcher
  - Scans folders for images below a user-defined minimum width × height
  - Pure PIL implementation (no OpenCV, no CLIP, no GPU) — fastest scanner in PhotoSift
  - Separate W × H spinboxes with 480p / 720p HD / 1080p FHD preset buttons
  - Seven quality categories: Tiny / Low / SD / HD / Full HD / High Res / Ultra HD
  - Results show actual pixel dimensions per image (e.g., "1024 × 768 (SD)")
  - Full thumbnail grid, zoom controls, select/clean flow — consistent with all other tools
  - Details documented in `LOW_RESOLUTION_DETECTOR.md`
- **test_dark_detection.py** — 27 new tests for Dark Photo Detection (feature previously had zero test coverage)
  - 17 unit tests covering quality boundaries, thresholds, batch function signatures, empty folder, Trash exclusion, result dict keys
  - 10 integration tests using synthetic PIL images written to disk

### Fixed
- **CommonUI.py** — `img._getexif()` replaced with `img.getexif()` (deprecated private PIL API removed in Pillow 8+)
- **DarkImageDetectionGUI.py** — `get_thumbnail()` returning `None` caused `AttributeError` crash (`img_tk.width()` on None); added None guard with "No Preview" placeholder canvas
- **DarkImageDetectionGUI.py** — missing `img_canvas.image = img_tk` reference caused PhotoImage garbage collection (blank thumbnails)
- **DarkImageDetectionGUI.py** — bare `except:` clause replaced with `except Exception:` (was silently catching `SystemExit` / `KeyboardInterrupt`)
- **BlurryImageDetectionGUI.py** — same `get_thumbnail()` None crash as above; added None guard with placeholder canvas
- **DuplicateImageIdentifier.py** — accidental duplicate code block loaded CLIP model at import time, overriding lazy loading and causing the full ~350 MB model to load on every `import DuplicateImageIdentifier`

### Test fixes
- **test_duplicate_detection.py** — `test_empty_image_list` incorrectly asserted `isinstance(result, dict)`; `get_clip_embedding_batch` returns `numpy.ndarray`; updated assertion to `np.ndarray` with `result.shape[0] == 0`
- **test_image_classification.py** — `test_confidence_score_range` contained only `self.assertTrue(True)` (placeholder); replaced with a real softmax bounds check

### Documentation
- Added `docs/code_review_v1.6.0.md` — full code review report covering all five bugs and test coverage changes
- Added `docs/LOW_RESOLUTION_DETECTOR.md` — design document for the new Low Resolution Detector feature

## [1.4.0] - 2025-10-19

### Added
- **Shared FileOperations Class**: Centralized file operations across all GUI applications
  - Reduced code duplication by ~230 lines
  - Unified file moving and completion popup logic
  - Improved maintainability and consistency

### Changed
- **UI Standardization**: Consistent window titles, button styling, and layout across all applications
  - All GUIs now prefixed with "PhotoSift" in window titles
  - Unified button colors (Blue for actions, Red for destructive operations)
  - Improved sidebar spacing and visual hierarchy
  - Enhanced launcher window visibility in taskbar

### Technical
- **Code Refactoring**: Refactored file operations to use shared utilities
- **Build System**: Updated version management across all build scripts
- **Error Handling**: Consistent error handling and user feedback

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
