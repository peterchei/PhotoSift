# PhotoSift v1.6.0 Release Notes

**Release Date:** TODO (e.g., January 21, 2026)

> Draft placeholder – fill in the concrete features/fixes before publishing. Keep wording concise and user-focused.

## ✨ Highlights
- TODO: Feature 1 (what it does, why users care)
- TODO: Feature 2
- TODO: Performance/UX improvement

## 🎨 UI & UX
- TODO: Notable UI changes (colors/layout/flows), reference key files (e.g., src/CommonUI.py, GUI modules).

## 🔧 Technical Changes
- Version bumped to 1.6.0 across build and package metadata (setup.py, pyproject.toml, version_info.txt, create_store_package.bat).
- TODO: Note any refactors, dependency updates, model changes, or new paths/flags relevant to PyInstaller packaging.

## 🐛 Fixes
- TODO: List fixes with brief user impact (e.g., crashes, incorrect detections, path handling).

## 📦 Packaging
- Build outputs: `dist/PhotoSift.exe`, `Output/PhotoSift_Setup.exe`, `PhotoSift.msix` (via create_store_package.bat + makeappx).
- AppX manifest version set to 1.6.0.0.
- TODO: Add any asset changes (store icons, resources) or installer script tweaks.

### Build Commands (Windows, from repo root)
- Standalone + installer: `.uild.bat`
- Store assets + package: `python create_store_assets.py && .\create_store_package.bat && makeappx pack /d store_package /p PhotoSift.msix`
	- Update `makeappx` path if SDK version differs (e.g., `C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe`).
- Optional signing: `signtool sign /fd SHA256 /a /f <cert.pfx> PhotoSift.msix`

### Checksums (SHA256)
- PhotoSift.exe: 084574060a4fe48a4800aab804b1efcc351024ac8ca60b57f2093924d59c9592
- PhotoSift_Setup.exe: 96b7e17943895ae957bcc5d3dbe4b2961f9f19f6a12eaea2de54e54f49b8411d
- PhotoSift.msix: a90cfb9c8de3c83243e593a61dc06d6666bb77f1ea7acdf261284cac393c3e8f

### Sizes (approx.)
- PhotoSift.exe: ~620 MB (620,038,464 bytes)
- PhotoSift_Setup.exe: ~620 MB (619,676,806 bytes)
- PhotoSift.msix: ~618 MB (618,196,659 bytes)

## 🧪 Testing
- TODO: Summarize test coverage executed (e.g., `python -m unittest discover -s tests -p "test_*.py" -v`, manual GUI smoke, model download check).

## 🚀 Upgrade Notes
- Backward compatibility: TODO (note if any behavior/threshold defaults changed).
- Migration: TODO (any data/config moves?).

## 📥 Download
- TODO: Add GitHub release tag link once published.
- Attach: PhotoSift.exe, PhotoSift_Setup.exe, PhotoSift.msix, checksums.

---
Use this template to finalize the 1.6.0 announcement; remove TODO lines before publishing.
