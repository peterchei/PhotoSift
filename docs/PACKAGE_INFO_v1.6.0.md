# PhotoSift Package Info v1.6.0

> Draft scaffold — fill sizes, checksums, and any installer/MSIX specifics after build.

## Artifacts
- Portable EXE: `PhotoSift.exe` (dist/)
- Installer: `PhotoSift_Setup.exe` (Output/)
- MSIX: `PhotoSift.msix` (store_package/ via makeappx)

## Sizes (approx.)
- PhotoSift.exe: ~620 MB (620,038,464 bytes)
- PhotoSift_Setup.exe: ~620 MB (619,676,806 bytes)
- PhotoSift.msix: ~618 MB (618,196,659 bytes)

## SHA256 Checksums
- PhotoSift.exe: 084574060a4fe48a4800aab804b1efcc351024ac8ca60b57f2093924d59c9592
- PhotoSift_Setup.exe: 96b7e17943895ae957bcc5d3dbe4b2961f9f19f6a12eaea2de54e54f49b8411d
- PhotoSift.msix: a90cfb9c8de3c83243e593a61dc06d6666bb77f1ea7acdf261284cac393c3e8f

## System Requirements
- Windows 10 1903+ or Windows 11
- Python not required for packaged builds
- Recommended: 8 GB RAM, ~2 GB free disk

## Build/Packaging Commands
- Desktop exe + installer: `.uild.bat`
- Store assets + MSIX: `python create_store_assets.py && .\create_store_package.bat && makeappx pack /d store_package /p PhotoSift.msix`
- Optional signing: `signtool sign /fd SHA256 /a /f <cert.pfx> PhotoSift.msix`

## Versioning
- Assembly/AppX: 1.6.0.0
- Python package metadata: 1.6.0

## Notes
- PyInstaller spec: PhotoSift.spec
- Store manifest generated inside create_store_package.bat; ensure Assets/ are regenerated when icons change.
- Update this file and release notes with final sizes/checksums before publishing.
