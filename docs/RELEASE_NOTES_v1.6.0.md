# PhotoSift v1.6.0 Release Notes

**Release Date:** 2026-02-22

---

## Highlights

- **New tool: Low Resolution Detector** — instantly flags images below a chosen pixel dimension threshold (no AI or GPU required, fastest scanner in PhotoSift)
- **5 bug fixes** across 4 source files, including 2 critical crash fixes and a model-loading performance fix
- **27 new automated tests** for Dark Photo Detection (previously had zero test coverage)

---

## New Feature: Low Resolution Detector

PhotoSift now has a fifth tool accessible from the launcher menu.

### What it does

Scans a folder and flags images whose pixel width or height falls below a user-defined minimum. Useful for:
- Finding accidental thumbnail saves mixed into a high-resolution library
- Identifying low-quality downloads or web-scraped images
- Sorting old low-resolution camera photos from modern high-res shots

### How to use it

1. Click **🔬 Detect Low Resolution Photos** in the launcher
2. Click **Select Folder** to choose your image folder
3. Set your minimum resolution using the **W** (width) and **H** (height) spinboxes, or click a preset:
   - **480p** — flag images below 640 × 480
   - **720p** (default) — flag images below 1280 × 720
   - **1080p** — flag images below 1920 × 1080
4. Click **Start Scan**
5. Review results in the thumbnail grid — low-resolution images show their actual dimensions in red (e.g., `"320 × 240 (SD)"`)
6. Select images to remove and click **Clean** to move them to the Trash folder

### Resolution quality categories

| Category | Shorter side | Example |
|----------|-------------|---------|
| Tiny | < 240 px | Web icons, app thumbnails |
| Low | 240–479 px | Old 240p mobile photos |
| SD | 480–719 px | Standard definition (480p) |
| HD | 720–1079 px | HD ready (720p) |
| Full HD | 1080–1439 px | Full HD (1080p) |
| High Res | 1440–2159 px | 2K / QHD |
| Ultra HD | ≥ 2160 px | 4K and above |

### Performance

This scanner reads only the image file header to get dimensions — no pixel decoding occurs. It is the fastest scanner in PhotoSift and scales linearly with folder size.

---

## Bug Fixes

### Critical — application crashes

**`DarkImageDetectionGUI.py` and `BlurryImageDetectionGUI.py` — thumbnail crash**

When an image could not be loaded (corrupt file, locked file, unsupported format), `get_thumbnail()` returned `None`. Code downstream immediately called `img_tk.width()` on that `None`, causing an `AttributeError` crash that closed the entire result view.

*Fix:* Added a `None` guard around all `img_tk.width()` calls. When the thumbnail cannot be loaded, a "No Preview" placeholder canvas is shown instead. Also added `img_canvas.image = img_tk` to prevent Python's garbage collector from blanking thumbnails that appeared to load correctly (a subtle Tkinter `PhotoImage` lifetime bug).

### Critical — CLIP model loaded on every import

**`DuplicateImageIdentifier.py` — accidental eager model load**

A duplicate code block at the module level called `CLIPModel.from_pretrained(...)` at import time, immediately overwriting the `model = None` lazy-load guard. Every Python import of `DuplicateImageIdentifier` triggered a full ~350 MB model download/load, even when duplicates were not being scanned.

*Fix:* Removed the duplicate block. The module now correctly delays model loading until `get_clip_embedding_batch()` or `get_clip_embedding()` is first called.

### High — deprecated PIL API

**`CommonUI.py` — `img._getexif()` → `img.getexif()`**

`Image._getexif()` is a private method that was removed in newer versions of Pillow. The public replacement `Image.getexif()` has been available since Pillow 8.0 (2021).

*Fix:* Replaced the private call with the public API.

### Medium — bare `except:` clause

**`DarkImageDetectionGUI.py` — `except:` catching system signals**

A bare `except:` clause in `get_thumbnail()` silently caught `SystemExit` and `KeyboardInterrupt`, making the application impossible to terminate normally in some conditions.

*Fix:* Changed to `except Exception:`.

---

## Test Coverage

### New test file: `tests/test_dark_detection.py`

Dark Photo Detection had no automated tests. A full test suite of 27 tests was added:

- **17 unit tests** — quality boundary values (Very Dark / Dark / Dim / Good / Bright / Very Bright / Unknown), threshold structure and ordering, batch function signature, empty folder handling, Trash exclusion, result dict key set
- **10 integration tests** — HSV channel validation on synthetic images, end-to-end `is_dark()` classification, batch scan detection, `(path, score)` tuple structure, brightness score bounds, missing-file sentinel, parallel processing

### Test suite totals

| Version | Tests | Failures |
|---------|-------|---------|
| v1.5.0 | 62 | 2 (pre-existing import errors) |
| v1.6.0 | 89 | 2 (same pre-existing import errors, unchanged) |

The 2 pre-existing errors are `test_button_colors` and `test_launcher_fixes` — both are `unittest.loader._FailedTest` import errors unrelated to application logic, present before and after this release.

### Existing test fixes

- `tests/test_duplicate_detection.py` — `test_empty_image_list` was asserting `isinstance(result, dict)` but `get_clip_embedding_batch` returns `numpy.ndarray`. Updated to assert `np.ndarray` with `result.shape[0] == 0`.
- `tests/test_image_classification.py` — `test_confidence_score_range` contained only `self.assertTrue(True)`. Replaced with a softmax bounds check asserting all probabilities ∈ [0, 1] and sum to 1.0.

---

## UI Changes

- Launcher window height expanded from 400 px to 450 px to accommodate the fifth button
- New purple button added to launcher: **🔬 Detect Low Resolution Photos** (`#8b5cf6`)

---

## Technical Changes

- Added `src/LowResolutionDetection.py` — pure PIL logic module, no cv2 / torch / transformers dependencies
- Added `src/LowResolutionGUI.py` — Tkinter GUI following the standard PhotoSift GUI pattern
- Modified `src/launchPhotoSiftApp.py` — new `launch_low_res_detector()` function, new button, adjusted window geometry

---

## Documentation

- `docs/code_review_v1.6.0.md` — full code review report for all four PhotoSift features
- `docs/LOW_RESOLUTION_DETECTOR.md` — design document for the new Low Resolution Detector

---

## Packaging

Build outputs: `dist/PhotoSift.exe`, `Output/PhotoSift_Setup.exe`, `PhotoSift.msix` (via `create_store_package.bat` + `makeappx`).

`LowResolutionDetection.py` and `LowResolutionGUI.py` require no new data files or model bundles — no `PhotoSift.spec` changes are needed for the new feature.

### Build Commands (Windows, from repo root)

```bat
rem Standalone + installer
build.bat

rem Store assets + package
python create_store_assets.py && create_store_package.bat
makeappx pack /d store_package /p PhotoSift.msix
```

---

## Upgrade Notes

- No breaking changes to existing features or threshold defaults
- No configuration migration needed
- The new Low Resolution Detector button appears automatically in the launcher on first run
