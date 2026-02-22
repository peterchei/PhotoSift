# Low Resolution Detector — Feature Design

**Added in:** v1.7.0 (development branch: Release_1_6_0)
**Author:** Claude Code (claude-sonnet-4-6)
**Files:** `src/LowResolutionDetection.py`, `src/LowResolutionGUI.py`, `tests/test_low_resolution.py`

---

## Overview

The Low Resolution Detector scans a folder for images whose pixel dimensions fall below a user-defined minimum width × height. It is useful for identifying:

- Accidental thumbnail saves mixed into a full-resolution library
- Low-quality downloads or web-scraped images
- Old camera photos taken at low resolution alongside modern high-resolution ones

Unlike the Blur and Dark detectors, this feature requires **no AI, no OpenCV, and no GPU**. PIL reads only the image file header to retrieve dimensions — making it the fastest scanner in PhotoSift.

---

## Architecture

The feature follows the standard PhotoSift **logic + GUI paired module pattern**:

```
src/LowResolutionDetection.py   ← Pure logic, no UI dependencies
src/LowResolutionGUI.py         ← Tkinter GUI, imports from logic module
tests/test_low_resolution.py    ← Unit + integration tests
src/launchPhotoSiftApp.py       ← Launcher entry point (modified)
```

### Why Pure PIL?

```
Feature          | Technology          | Speed factor
─────────────────┼─────────────────────┼──────────────
Classification   | CLIP + GPU          | slowest
Duplicate        | CLIP + cosine sim   | slow
Blur             | OpenCV Laplacian    | medium
Dark             | OpenCV HSV          | medium
Low Resolution   | PIL header read     | fastest ✓
```

PIL's `Image.open()` uses lazy loading — `img.size` reads only the file header (a few hundred bytes), never decoding pixel data. A folder of 1,000 images scans in under a second on typical hardware.

---

## Logic Module: `LowResolutionDetection.py`

### `LowResolutionDetector` class

```python
class LowResolutionDetector:
    def __init__(self, min_width=1280, min_height=720)
```

**Default threshold:** 1280 × 720 (720p HD). An image is flagged if either dimension is below the minimum — i.e., it fails on width **or** height, not requiring both to fail.

| Method | Returns | Description |
|--------|---------|-------------|
| `get_dimensions(path)` | `(int, int)` | Width, height. Returns `(-1, -1)` on any error. |
| `is_low_res(path)` | `(bool, int, int)` | Flag + actual dimensions. Returns `(False, -1, -1)` on error (don't flag unreadable files). |
| `get_resolution_quality(w, h)` | `str` | Human-readable quality category based on the shorter side. |

### Resolution quality scale

Quality is based on the **shorter side** (the limiting dimension), which maps naturally to familiar display standards:

| Category | Shorter side | Typical use |
|----------|-------------|-------------|
| Tiny     | < 240 px    | Icons, web thumbnails |
| Low      | 240–479 px  | Old mobile photos, 240p video |
| SD       | 480–719 px  | Standard definition (480p) |
| HD       | 720–1079 px | HD ready (720p) |
| Full HD  | 1080–1439 px | Full HD (1080p) |
| High Res | 1440–2159 px | 2K / QHD |
| Ultra HD | ≥ 2160 px   | 4K and above |
| Unknown  | -1          | File could not be read |

### `detect_low_res_images_batch()` function

```python
def detect_low_res_images_batch(
    folder_path,
    min_width=1280,
    min_height=720,
    progress_callback=None,
    max_workers=None,       # defaults to min(cpu_count, 8)
) -> dict
```

**Return value:**

```python
{
    'low_res_images': [(path, width, height), ...],  # sorted smallest first
    'ok_images':      [(path, width, height), ...],  # sorted largest first
    'total_processed': int,
    'total_low_res':   int,
}
```

Note: result tuples are **3-elements** `(path, width, height)` — distinct from the 2-element `(path, score)` tuples used in Dark and Blur detection. This is intentional because two dimensions (width + height) are both meaningful, not reducible to a single scalar.

**Sorting:**
- `low_res_images`: ascending by `min(width, height)` — worst (smallest) images first
- `ok_images`: descending by `min(width, height)` — best (largest) images first

**Concurrency:** Uses `ThreadPoolExecutor` with `as_completed()` for parallel header reads. Worker count defaults to `min(cpu_count, 8)` following the same cap used by Blur and Dark detection.

**Trash exclusion:** Skips any path where `'Trash'` appears in `Path.parts`, consistent with all other PhotoSift scanners.

**Deduplication:** Extension scanning is done for both lowercase and uppercase variants (e.g., `.jpg` and `.JPG`), then `list(set(...))` removes any cross-matches.

### `get_recommended_thresholds()` function

```python
{
    'minimal': {'value_w': 640,  'value_h': 480,  'label': '480p',     'description': '...'},
    'normal':  {'value_w': 1280, 'value_h': 720,  'label': '720p HD',  'description': '...'},
    'strict':  {'value_w': 1920, 'value_h': 1080, 'label': '1080p FHD','description': '...'},
}
```

---

## GUI Module: `LowResolutionGUI.py`

### Class: `LowResolutionApp`

Inherits the full layout from `DarkImageDetectionGUI.py` with these key adaptations:

#### Threshold controls

Dark detection uses a single float slider (0–150). Low resolution detection exposes **two integer dimensions** because width and height are independently meaningful. The sidebar contains:

```
┌─────────────────────────────────┐
│ Minimum Resolution              │
│                                 │
│  W: [1280]  H: [720]           │
│                                 │
│  [ 480p ]  [ 720p ]  [ 1080p ] │
└─────────────────────────────────┘
```

- `W` / `H` spinboxes (range 1–9999) with `tk.IntVar` backing
- Three preset buttons wire directly to `_apply_preset(w, h)` which sets both vars

#### Tree categories

| Category ID | Label | Contents |
|-------------|-------|----------|
| `"low_res"` | Low Resolution | Images below threshold (worst first) |
| `"ok"` | OK Resolution | Images at or above threshold (best first) |

The default selection after scan is always `"low_res"` (same pattern as Dark detection selecting `"dark"` first).

#### Per-image label

Dark detection shows: `"Brightness: 45.2 (Dark)"`
Low resolution shows: `"1024 × 768 (SD)"`

Color coding:
- Red (`colors['danger']`) for low-resolution images
- Green (`colors['success']`) for OK images

#### Data structures

```python
self.low_res_images = []   # list of (path, width, height)
self.ok_images = []        # list of (path, width, height)
self.dimensions = {}       # {path: (width, height)}
```

The `dimensions` dict is populated on `on_scan_complete()` from both lists so `display_page()` can look up any path regardless of category.

#### Thumbnail handling

Identical to Dark detection (`get_thumbnail()` with `Image.Resampling.LANCZOS`, LRU via `image_cache`, `img_canvas.image = img_tk` GC reference, `None` guard with "No Preview" fallback canvas).

#### Clean operation

After moving selected files to Trash, `on_scan_complete()` is called with the filtered lists to refresh the tree and thumbnails. The full `(path, w, h)` tuples are preserved through the filter:

```python
'low_res_images': [(p, w, h) for p, w, h in self.low_res_images if p not in selected_paths],
'ok_images':      [(p, w, h) for p, w, h in self.ok_images      if p not in selected_paths],
```

---

## Launcher Integration: `launchPhotoSiftApp.py`

### Window height

Expanded from `500x400` to `500x450` to accommodate the fifth button without crowding.

### New function: `launch_low_res_detector()`

Follows the identical pattern as `launch_dark_detector()`:

```python
def launch_low_res_detector():
    selection_window.destroy()
    try:
        from LowResolutionGUI import LowResolutionApp
        app_root = tk.Tk()
        app = LowResolutionApp(app_root)
        app_root.mainloop()
        show_app_selection()
    except Exception as e:
        print(f"Error launching LowResolutionGUI: {e}")
        import traceback
        traceback.print_exc()
        show_app_selection()
```

No preload section changes are needed — this feature loads no AI models.

### New button

```
Color: #8b5cf6 (purple) / active: #7c3aed
Text:  🔬 Detect Low Resolution Photos
```

Purple was chosen to avoid conflict with the four existing button colors (blue, green, orange, slate).

**Final launcher button set:**

```
┌───────────────────────────────────┐
│  PhotoSift                        │
│  Choose your image management tool│
│                                   │
│  [🧹 Identify Unwanted Photos   ] │  ← blue    #3b82f6
│  [🔍 Identify Duplicate Photos  ] │  ← green   #10b981
│  [🌫️ Detect Blurry Photos       ] │  ← orange  #f97316
│  [🌑 Detect Dark Photos         ] │  ← slate   #64748b
│  [🔬 Detect Low Resolution Photos] │  ← purple  #8b5cf6  ← NEW
└───────────────────────────────────┘
```

---

## Test Coverage: `tests/test_low_resolution.py`

27 tests across two classes, modelled on `tests/test_dark_detection.py`.

### `TestLowResolutionDetection` — 17 unit tests (no file I/O)

| Test | What it verifies |
|------|-----------------|
| `test_detector_initialization` | `min_width` / `min_height` stored correctly |
| `test_threshold_customization` | Custom constructor values retained |
| `test_recommended_thresholds_function` | Returns dict with `minimal`/`normal`/`strict` keys |
| `test_recommended_thresholds_ordering` | `minimal_w < normal_w < strict_w` |
| `test_resolution_quality_tiny` | short < 240 → "Tiny" |
| `test_resolution_quality_low` | 240–479 → "Low" |
| `test_resolution_quality_sd` | 480–719 → "SD" |
| `test_resolution_quality_hd` | 720–1079 → "HD" |
| `test_resolution_quality_full_hd` | 1080–1439 → "Full HD" |
| `test_resolution_quality_high_res` | 1440–2159 → "High Res" |
| `test_resolution_quality_ultra_hd` | ≥ 2160 → "Ultra HD" |
| `test_resolution_quality_error_sentinel` | (-1, -1) → "Unknown" |
| `test_batch_detection_function_exists` | `detect_low_res_images_batch` is callable |
| `test_batch_detection_signature` | Has `folder_path`, `min_width`, `min_height` params |
| `test_empty_folder_handling` | Empty dir → correct dict shape, all counts 0 |
| `test_trash_folder_exclusion` | `'Trash' in Path.parts` logic validated |
| `test_result_dict_keys` | Exactly `{low_res_images, ok_images, total_processed, total_low_res}` |

### `TestLowResolutionDetectionIntegration` — 10 integration tests (synthetic PIL images)

| Test | What it verifies |
|------|-----------------|
| `test_low_res_image_correctly_flagged` | 200×150 PNG → `is_low_res()` returns `(True, 200, 150)` |
| `test_ok_image_not_flagged` | 1920×1080 PNG → returns `(False, 1920, 1080)` |
| `test_get_dimensions_returns_correct_size` | 640×480 PNG → `get_dimensions()` returns `(640, 480)` |
| `test_get_dimensions_on_missing_file` | Non-existent path → `(-1, -1)` |
| `test_is_low_res_on_missing_file` | Non-existent path → `(False, -1, -1)` |
| `test_batch_detects_low_res_image` | Batch scan finds 200×150 PNG in `low_res_images` |
| `test_batch_result_tuple_structure` | Entries are `(str, int, int)` 3-tuples |
| `test_result_sorted_smallest_first` | Multiple sizes → sorted ascending by `min(w,h)` |
| `test_parallel_processing_support` | `cpu_count > 0` |
| `test_module_imports` | PIL, pathlib, concurrent.futures importable |

### Test infrastructure notes

- `sys.stdout.reconfigure(encoding='utf-8')` at top to handle ✓ character on Windows cp1252 terminals
- Integration tests write PNG files using `PIL.Image.new("RGB", (w, h))` (not numpy arrays, to avoid byte ordering concerns and Pillow deprecation warnings)
- Each test that writes files uses an isolated subdirectory with `shutil.rmtree` cleanup before `mkdir` to prevent cross-test contamination from prior runs

---

## Design Decisions

### Flag on width OR height (not AND)

An image is flagged if `width < min_width OR height < min_height`. This catches both portrait and landscape images that are below standard in either dimension. Using AND would miss portrait images that are wide enough but not tall enough.

### Separate width and height controls (not a single "megapixel" value)

A single megapixel slider (e.g., "flag below 1 MP") would group 1280×780 and 1000×1000 together despite having very different practical utility. Separate W/H spinboxes let users express real standards (1280×720, 1920×1080) that align with display and printing workflows.

### Error sentinel is `(-1, -1)` not raising an exception

Consistent with Dark detection's `-1` score sentinel. Unreadable files are silently skipped (counted as "processed" but not included in either result list). This prevents one corrupt file from aborting a large batch scan.

### No "total_ok" in result dict

`total_processed = total_low_res + len(ok_images)`. A separate `total_ok` key would be redundant and inconsistent with Dark detection's result shape.

---

## Comparison with Similar Features

| Aspect | Dark Detection | Blur Detection | Low Res Detection |
|--------|---------------|----------------|-------------------|
| Algorithm | HSV Value mean | Laplacian variance | PIL header read |
| Score type | float 0–255 | float 0–∞ | (int, int) dimensions |
| Threshold control | Single slider | Single slider | W + H spinboxes |
| Presets | strict/normal/lenient | strict/normal/lenient | 480p/720p/1080p |
| OpenCV required | Yes | Yes | **No** |
| GPU optional | No | No | No |
| Speed | Medium | Medium | **Fastest** |
| Result sort | Score ascending | Score ascending | Short-side ascending |

---

## How to Run

```bash
# Logic module tests only
python tests/test_low_resolution.py

# Full test suite
python -m unittest discover -s tests -p "test_*.py" -v

# Launch the full app (includes the new button)
python src/launchPhotoSiftApp.py

# Run the GUI directly (for development)
python src/LowResolutionGUI.py
```
