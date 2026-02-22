# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is PhotoSift

Windows desktop GUI app (tkinter + PyInstaller) for AI-powered photo management. The launcher (`src/launchPhotoSiftApp.py`) routes to four tools: image classification, duplicate detection, blur detection, and dark photo detection.

## Commands

**Run locally:**
```bash
pip install -e .
python src/launchPhotoSiftApp.py        # full launcher menu
python src/DuplicateImageIdentifierGUI.py  # individual tool directly
```

**Tests:**
```bash
python -m unittest discover -s tests -p "test_*.py" -v
# or
python tests/run_all_tests.py
```
Tests assume `src` on `PYTHONPATH`, may download CLIP on first use, and create `tests/test_data/` fixtures.

**Build:**
```bash
.\build.bat   # creates build_env, runs PyInstaller, optionally Inno Setup → Output/
```

**Store packaging:**
```bash
.\create_store_package.bat   # see docs/ms-store-submission.md
```

## Architecture

### Module split pattern
Each tool pairs a GUI file and logic file in `src/`:
- `ImageClassifierGUI.py` + `ImageClassification.py` — CLIP text-image matching (people vs screenshots)
- `DuplicateImageIdentifierGUI.py` + `DuplicateImageIdentifier.py` — CLIP embeddings + cosine similarity matrix
- `BlurryImageDetectionGUI.py` + `BlurryImageDetection.py` — Laplacian variance with quality buckets
- `DarkImageDetectionGUI.py` + `DarkImageDetection.py` — HSV Value channel mean

Keep logic testable and UI-thin. New tools should follow the same paired module pattern.

### Shared UI (`src/CommonUI.py`)
Reuse `ModernColors`, `ModernButton`, `ProgressWindow`, `ToolTip`, zoom controls, and status bar helpers. Do not create ad-hoc widgets when these exist.

### Startup / PyInstaller quirks
Entrypoints need `multiprocessing.freeze_support()` and `sys._MEIPASS` path handling near the top. Launcher logs to `%LOCALAPPDATA%/PhotoSift/logs/` and adds `application_path` to `sys.path`.

### Model handling
CLIP (`openai/clip-vit-base-patch32`) loads lazily, preferring local bundle at `models/clip-vit-base-patch32/` when frozen, otherwise downloads from HuggingFace. Keep new model loads behind helpers and compatible with `sys._MEIPASS` resource paths.

### Concurrency
Batch operations use `ThreadPoolExecutor` capped at `min(cpu_count, 8)` workers. Never block the UI thread—use background threads with progress callbacks and `widget.after(...)`. Duplicate detection builds a full similarity matrix; avoid O(n²) extensions unless gated by thresholds.

### Key invariants to preserve
- **Trash safety**: Scans skip `Trash` subdirectories; prefer move-to-trash over delete.
- **Unicode paths**: Use PIL for image loads (not `cv2.imread`) to maintain Unicode path support.
- **Detection thresholds/sorting**: Don't change threshold semantics or sort order without updating all callers.
- **`IMG_EXT` set**: Use the existing extension set for file filtering.
- **Device selection**: `cuda` if available, CPU fallback—never hardcode GPU paths.
- **PyInstaller-safe imports**: No dynamic module names; add new data files to `resources/` or `models/` and update `PhotoSift.spec`.
- **Python 3.8+ / Windows**: Avoid POSIX-only paths in core flows.
