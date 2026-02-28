# Safe Content Scanner — Feature Design

**Added in:** v1.8.0 (development branch: V7_LowResolutionDetection)
**Author:** Claude Code (claude-sonnet-4-6)
**Files:** `src/SafeContentDetection.py`, `src/SafeContentDetectionGUI.py`, `tests/test_safe_content_detection.py`

---

## Overview

The Safe Content Scanner uses the CLIP AI model (already bundled in PhotoSift) to classify images into four content categories: **Safe**, **Adult**, **Violent / Gore**, and **Disturbing**. It is designed to help parents and guardians audit a shared photo library before letting children browse it.

All processing is **entirely local** — no images or data are sent to the internet. Because CLIP is already included in the PhotoSift executable, most users will not need any additional download.

---

## Use Cases

- Auditing a family photo library before sharing with children
- Reviewing downloaded or scraped image collections for inappropriate content
- Identifying accidentally-saved adult or violent content mixed into a personal library
- A first-pass content filter before manual review

---

## Architecture

The feature follows the standard PhotoSift **logic + GUI paired module pattern**:

```
src/SafeContentDetection.py      ← Pure logic, no UI dependencies
src/SafeContentDetectionGUI.py   ← Tkinter GUI, imports from logic module
tests/test_safe_content_detection.py  ← Unit tests (no CLIP load required)
src/launchPhotoSiftApp.py        ← Launcher entry point (modified)
```

### Technology choice — why CLIP?

| Option | Categories | Extra download | Notes |
|--------|-----------|---------------|-------|
| **CLIP (chosen)** | 4 (safe/adult/violent/disturbing) | None — already bundled | Zero-shot, general-purpose |
| Dedicated NSFW model (e.g. Falconsai) | 2 (safe/nsfw) | ~200 MB | Binary only, misses violent/disturbing |
| OpenCV heuristics | N/A | None | Cannot classify content semantics |

CLIP handles all four categories in a single forward pass using text-image matching. No additional model files are needed.

### CLIP text-prompt approach

CLIP scores an image against a list of text descriptions. PhotoSift groups the descriptions by category and sums probabilities per group to produce a category score:

```
text prompts ──► CLIP ──► softmax probabilities ──► sum per category ──► winning label
```

More prompts per category improve robustness by covering more semantic variations. The existing people/screenshot classifier uses 11–12 prompts per category; Safe Content Scanner uses 8–10.

---

## Logic Module: `SafeContentDetection.py`

### `LABELS` dictionary

```python
LABELS = {
    "safe":       [10 prompts],   # family-friendly, nature, food, events, ...
    "adult":      [ 8 prompts],   # explicit content, nudity, sexual imagery, ...
    "violent":    [ 8 prompts],   # gore, injuries, combat, accidents, ...
    "disturbing": [ 8 prompts],   # drugs, crime, self-harm, extremist imagery, ...
}
```

Total: **34 text prompts** across 4 categories.

### `SafeContentDetector` class

```python
class SafeContentDetector:
    def classify_image(self, image_path) -> tuple[str, float, dict]
    def get_content_rating(self, label: str, confidence: float) -> str
```

| Method | Returns | Description |
|--------|---------|-------------|
| `classify_image(path)` | `(label, confidence, all_scores)` | Run CLIP on a single image. Returns `('error', 0.0, {})` on failure. |
| `get_content_rating(label, confidence)` | `str` | Map label + confidence to a human-readable string. |

#### Content rating strings

| Label | Confidence ≥ 60% | Confidence < 60% |
|-------|-----------------|-----------------|
| `safe` | `"Safe"` | `"Likely Safe"` |
| `adult` | `"Adult Content"` | `"Possibly Adult"` |
| `violent` | `"Violent / Gore"` | `"Possibly Violent"` |
| `disturbing` | `"Disturbing"` | `"Possibly Disturbing"` |

The 60% threshold is where CLIP transitions from uncertain to reasonably confident classification on this prompt set.

### `scan_content_batch()` function

```python
def scan_content_batch(
    image_paths,
    progress_callback=None,
    batch_size=32,
) -> list[tuple[str, str, float, dict]]
```

**Returns:** list of `(path, label, confidence, all_scores)` tuples.
Failed images return `(path, 'error', 0.0, {})`.

**Implementation details:**
- Images are loaded in parallel using `ThreadPoolExecutor(max_workers=8)` and resized to 224×224 for CLIP
- Text prompts are tokenised once per call (not per image) — the same token tensor is broadcast across all images in each batch
- `logits_per_image.softmax(dim=-1)` gives probability across all 34 prompts; these are summed per-label owner to produce a 4-element score vector
- `torch.autocast` (float16 on CUDA, ignored on CPU) is used for inference efficiency
- Results are reconstructed in original input order

### `scan_folder_safe_content()` function

```python
def scan_folder_safe_content(
    folder_path,
    progress_callback=None,
) -> dict
```

**Return value:**

```python
{
    'safe_images':       [(path, confidence, all_scores), ...],  # sorted desc by confidence
    'adult_images':      [(path, confidence, all_scores), ...],  # sorted desc by confidence
    'violent_images':    [(path, confidence, all_scores), ...],  # sorted desc by confidence
    'disturbing_images': [(path, confidence, all_scores), ...],  # sorted desc by confidence
    'error_images':      [path, ...],
    'total_processed':   int,
    'total_flagged':     int,   # adult + violent + disturbing count
}
```

Note: result tuples are **3-elements** `(path, confidence, all_scores)` — distinct from the 2-element `(path, score)` tuples in Dark/Blur detection. `all_scores` is a dict with all 4 category probabilities, preserving the full distribution for future display or filtering needs.

**Sorting:** All four image lists are sorted descending by confidence so the most clearly-flagged images appear first in the UI.

**Trash exclusion:** Skips paths where `'Trash'` appears in `Path.parts`, consistent with all other PhotoSift scanners.

### Model loading

Uses the identical lazy-load pattern from `ImageClassification.py`:

```python
model = None
processor = None

def load_models():
    global model, processor
    if model is None or processor is None:
        model_path = get_model_path()   # sys._MEIPASS → local models/ → HuggingFace
        model = CLIPModel.from_pretrained(model_path).to(device).eval()
        processor = CLIPProcessor.from_pretrained(model_path)
```

The model is not loaded at import time. It is loaded on the first call to `scan_content_batch()`, which happens inside the background thread — never on the UI thread.

---

## GUI Module: `SafeContentDetectionGUI.py`

### Class: `SafeContentDetectionApp`

Hybrid of `DarkImageDetectionGUI` (tree category switching, thumbnail grid, clean flow) and `ImageClassifierGUI` (CLIP progress feedback, multi-category result display).

### Sidebar layout

```
┌──────────────────────────────────┐
│  [Select Folder]                 │
│  /path/to/folder                 │
│                                  │
│  ⚠ AI screening — review flagged │
│    images manually before        │
│    deleting.                     │
│    Confidence below 60% is low.  │
│                                  │
│  [Start Scan]                    │
│                                  │
│  Categories                      │
│  ┌──────────────────┬──────┐     │
│  │ Adult Content    │  12  │     │
│  │ Violent / Gore   │   3  │     │
│  │ Disturbing       │   5  │     │
│  │ Safe Images      │ 230  │     │
│  └──────────────────┴──────┘     │
└──────────────────────────────────┘
```

### AI disclaimer widget

A persistent warning label sits between the folder selector and the scan button. It uses `colors['warning']` (amber) foreground to be visible without being alarming:

```
⚠ AI screening — review flagged
  images manually before deleting.
  Confidence below 60% is low.
```

This is mandatory — CLIP is a general vision-language model, not a content moderation specialist. False positives occur on artistic nudity, medical imagery, and cartoon violence.

### Tree categories

Tree entries are inserted in this order so flagged categories appear first:

| Tree ID | Label | Color cue |
|---------|-------|-----------|
| `"adult"` | Adult Content | danger (red) |
| `"violent"` | Violent / Gore | danger (red) |
| `"disturbing"` | Disturbing | warning (amber) |
| `"safe"` | Safe Images | success (green) |

After a scan completes, the tree automatically selects the most concerning non-empty category:
`adult` → `violent` → `disturbing` → `safe`

### Per-image score labels

```python
label_str = f"{label.title()}: {confidence * 100:.0f}%"
# e.g. "Adult: 82%", "Violent: 71%", "Disturbing: 65%", "Safe: 95%"

color = (colors['danger']  if label in ('adult', 'violent')
    else colors['warning'] if label == 'disturbing'
    else colors['success'])
```

### Data structures

```python
self.safe_images       = []  # [(path, confidence, all_scores), ...]
self.adult_images      = []
self.violent_images    = []
self.disturbing_images = []
self.content_scores    = {}  # {path: (label, confidence, all_scores)} — lookup for display_page()
```

### Scan thread flow

```
UI thread: progress_window.show() → Thread.start()

Background thread:
  1. progress_window.update(0, 1, "Loading AI model...", "Initializing CLIP...")
  2. scan_folder_safe_content(folder, progress_callback)
     ├─ scan_content_batch() → load_models() [first call only, ~5–15 s]
     └─ batched CLIP inference with progress callback
  3. root.after(0, on_scan_complete, results)

UI thread: on_scan_complete() → rebuild tree → show_thumbnails_for_category()
```

### Clean flow

Identical to Dark/Blur/LowRes GUI:

1. User checks thumbnails → "Clean (N)" button activates
2. `FileOperations.move_images_to_trash(selected_paths, self.folder)`
3. `on_scan_complete()` called with filtered lists (selected paths removed)
4. Tree and thumbnail grid refresh

**No auto-delete.** The scanner never removes files without explicit user action. This is especially important given the possibility of false positives.

---

## Launcher Integration: `launchPhotoSiftApp.py`

### Window height

Expanded from `500x450` to `500x500` to accommodate the sixth button without crowding.

### New function: `launch_safe_content_scanner()`

Follows the identical pattern as all other `launch_*` functions:

```python
def launch_safe_content_scanner():
    selection_window.destroy()
    try:
        from SafeContentDetectionGUI import SafeContentDetectionApp
        app_root = tk.Tk()
        app = SafeContentDetectionApp(app_root)
        app_root.mainloop()
        show_app_selection()
    except Exception as e:
        print(f"Error launching SafeContentDetectionGUI: {e}")
        import traceback
        traceback.print_exc()
        show_app_selection()
```

### New button

```
Color: #0891b2 (cyan-600 / teal) / active: #0e7490
Text:  🛡️ Safe Content Scanner
```

Teal was chosen to differentiate from the five existing button colors (blue, green, orange, slate, purple).

**Final launcher button palette (6 tools):**

```
┌─────────────────────────────────────┐
│  PhotoSift                          │
│  Choose your image management tool  │
│                                     │
│  [🧹 Identify Unwanted Photos     ] │  ← blue   #3b82f6
│  [🔍 Identify Duplicate Photos    ] │  ← green  #10b981
│  [🌫️ Detect Blurry Photos         ] │  ← orange #f97316
│  [🌑 Detect Dark Photos           ] │  ← slate  #64748b
│  [🔬 Detect Low Resolution Photos ] │  ← purple #8b5cf6
│  [🛡️ Safe Content Scanner         ] │  ← teal   #0891b2  ← NEW
└─────────────────────────────────────┘
```

---

## Test Coverage: `tests/test_safe_content_detection.py`

18 unit tests — no CLIP model load required during any test.

### `TestSafeContentDetection` — 18 unit tests

| Test | What it verifies |
|------|-----------------|
| `test_labels_dict_exists` | `LABELS` dict exists with exactly 4 keys |
| `test_labels_have_required_categories` | Keys are exactly `{safe, adult, violent, disturbing}` |
| `test_each_category_has_prompts` | Each category has ≥ 5 text prompts |
| `test_safe_prompts_are_strings` | All prompts are non-empty strings |
| `test_detector_class_exists` | `SafeContentDetector` is importable and instantiable |
| `test_classify_image_method_exists` | `SafeContentDetector().classify_image` is callable |
| `test_get_content_rating_method_exists` | `SafeContentDetector().get_content_rating` is callable |
| `test_scan_folder_function_exists` | `scan_folder_safe_content` is callable |
| `test_scan_folder_signature` | Has `folder_path` parameter |
| `test_result_dict_keys` | Result has exactly the 7 expected keys |
| `test_content_rating_safe` | `get_content_rating('safe', 0.9)` → `"Safe"` |
| `test_content_rating_adult` | `get_content_rating('adult', 0.8)` → `"Adult Content"` |
| `test_content_rating_violent` | `get_content_rating('violent', 0.7)` → `"Violent / Gore"` |
| `test_content_rating_disturbing` | `get_content_rating('disturbing', 0.6)` → `"Disturbing"` |
| `test_content_rating_low_confidence_safe` | `get_content_rating('safe', 0.51)` → `"Likely Safe"` |
| `test_softmax_confidence_bounds` | Softmax over 4 values sums to 1.0, each in [0, 1] |
| `test_empty_folder_handling` | Empty folder scan → all counts 0, correct dict shape |
| `test_trash_folder_exclusion` | Image in `Trash/` subdirectory is excluded from scan |

### Test infrastructure notes

- `sys.stdout.reconfigure(encoding='utf-8')` at top to handle ✓/→ characters on Windows cp1252 terminals
- Empty folder tests call `scan_folder_safe_content()` directly — model is never loaded because the early-return path (`if not image_paths: return result`) is hit first
- Trash exclusion test creates a real JPEG-format PNG with `PIL.Image.new("RGB", (100, 100))` to confirm path filtering, not CLIP inference

### Test suite totals

| Version | Tests | Failures |
|---------|-------|---------|
| v1.7.0  | 89    | 2 (pre-existing import errors) |
| v1.8.0  | 107   | 2 (same pre-existing errors, unchanged) |

---

## Design Decisions

### Why CLIP and not a dedicated NSFW model?

CLIP is already bundled in the PhotoSift EXE (~350 MB). A dedicated NSFW model (e.g. Falconsai/nsfw_image_detection) would require an additional download and only provides binary safe/nsfw classification. CLIP's zero-shot text-image matching covers all four categories — including violent and disturbing content that a pure NSFW model would miss — in a single forward pass.

### Why 4 categories instead of binary safe/unsafe?

A binary classifier tells the user only that something is flagged, not why. Four categories let the user prioritise review: adult content may warrant immediate action, while "disturbing" might include crime-scene news photos that are contextually fine. The tree UI makes this prioritisation visual.

### Accuracy expectations

CLIP is a general vision-language model trained on image-text pairs from the web, not a content moderation specialist. Expected accuracy:

- **Clear cases** (explicit adult content, graphic violence): ~85–90%
- **Edge cases** (artistic nudity, medical imagery, cartoon violence, dark humor): may be misclassified
- **Innocent images wrongly flagged**: possible — hence the mandatory AI disclaimer

The 60% confidence threshold helps distinguish between definitive classifications and uncertain ones. Images below 60% use hedged language ("Likely Safe", "Possibly Adult").

### No automatic deletion

The scanner never moves files to Trash without an explicit user action (checking a box and clicking Clean). This is especially important for a content scanner where false positives exist.

### `all_scores` preserved in result tuples

Each result tuple includes the full `{'safe': float, 'adult': float, ...}` score dict. This is not used in the current UI but preserves the complete CLIP output for potential future features (e.g., showing a score breakdown tooltip per image, or filtering by secondary category confidence).

---

## Comparison with Similar Features

| Aspect | Image Classifier | Duplicate Finder | Safe Content Scanner |
|--------|-----------------|-----------------|---------------------|
| Model | CLIP text-image | CLIP embeddings | CLIP text-image |
| Categories | 2 (people / screenshot) | N/A (similarity) | 4 (safe / adult / violent / disturbing) |
| Output | Classification + confidence | Similarity groups | Classification + confidence per image |
| GPU optional | Yes | Yes | Yes |
| Extra download | None (bundled) | None (bundled) | **None (bundled)** |
| Batch size | 32 | 32 | 32 |
| First-run model load | ~5–15 s | ~5–15 s | ~5–15 s |

---

## How to Run

```bash
# Unit tests (no CLIP load required — fast)
python -m unittest tests/test_safe_content_detection.py -v

# Full test suite
python -m unittest discover -s tests -p "test_*.py" -v

# Launch the full app (includes the new teal button)
build_env\Scripts\python.exe src/launchPhotoSiftApp.py

# Run the GUI directly (requires build_env Python for transformers/torch)
build_env\Scripts\python.exe src/SafeContentDetectionGUI.py
```

> **Note:** `transformers`, `torch`, and `Pillow` are installed only in `build_env`. Always use `build_env\Scripts\python.exe` (or activate with `build_env\Scripts\activate`) when running source directly.
