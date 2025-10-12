# PhotoSift Release Process

This document outlines the complete step-by-step process for creating a new PhotoSift release, including desktop deployment and Microsoft Store submission.

## 📋 Pre-Release Checklist

- [ ] All features tested and working
- [ ] Code reviewed and committed
- [ ] No critical bugs or issues
- [ ] Documentation updated
- [ ] Privacy policy reviewed (if changed)

## 🔢 Step 1: Version Management

### 1.1 Update Version Numbers

Update the version number in the following files:

#### **setup.py**
```python
version="X.X.X",  # Change to new version
```

#### **version_info.txt**
```python
filevers=(X, X, X, 0),    # Change version numbers
prodvers=(X, X, X, 0),    # Change version numbers
...
StringStruct(u'FileVersion', u'X.X.X'),      # Change version string
StringStruct(u'ProductVersion', u'X.X.X')    # Change version string
```

#### **pyproject.toml**
```toml
version = "X.X.X"  # Change to new version
```

#### **create_store_package.bat**
```batch
echo            Version="X.X.X.0" /^> >> "store_package\AppxManifest.xml"
```

### 1.2 Commit Version Updates
```bash
git add setup.py version_info.txt pyproject.toml create_store_package.bat
git commit -m "Bump version to X.X.X"
```

## 🏗️ Step 2: Build Desktop Packages

### 2.1 Build Standalone Executable and Installer
```bash
.\build.bat
```

**Expected Output:**
- `dist/PhotoSift.exe` (~550MB) - Standalone executable
- `Output/PhotoSift_Setup.exe` (~551MB) - Windows installer

### 2.2 Verify Build Success
```bash
# Check files exist and sizes
dir dist\PhotoSift.exe
dir Output\PhotoSift_Setup.exe

# Test executable runs
.\dist\PhotoSift.exe
```

## 🏪 Step 3: Build Microsoft Store Package

### 3.1 Create Store Assets
```bash
python create_store_assets.py
```

### 3.2 Build Store Package Structure
```bash
.\create_store_package.bat
```

### 3.3 Create MSIX Package
```bash
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift.msix
```

### 3.4 One-Command Store Build (Alternative)
```bash
python create_store_assets.py && .\create_store_package.bat && & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift.msix
```

**Expected Output:**
- `PhotoSift.msix` (~549MB) - Microsoft Store package
- `store_package/` directory with all package contents

### 3.5 Verify MSIX Package
```bash
# Check package version
type store_package\AppxManifest.xml | findstr "Version="

# Check package size
dir PhotoSift.msix
```

## 📝 Step 4: Create Release Documentation

### 4.1 Create Release Notes
Create `RELEASE_NOTES_vX.X.X.md` with:
- What's new in this version
- Bug fixes and improvements
- Technical changes
- Installation instructions

### 4.2 Create Package Information
Create `PACKAGE_INFO_vX.X.X.md` with:
- Package file descriptions
- System requirements
- Distribution options
- Security information

## 🏷️ Step 5: Git Tagging and Release

### 5.1 Create Git Tag
```bash
git tag -a vX.X.X -m "PhotoSift vX.X.X - [Brief description of major changes]

✨ Major Features:
- [List key features]

🎨 UI Improvements:
- [List UI changes]

🔧 Technical Enhancements:
- [List technical improvements]

This release maintains full backward compatibility while [describe main benefit]."
```

### 5.2 Push to Repository
```bash
git push origin master
git push origin vX.X.X
```

### 5.3 Create GitHub Release
1. Go to: https://github.com/peterchei/PhotoSift/releases
2. Click "Create a new release"
3. Select tag: `vX.X.X`
4. Title: `PhotoSift vX.X.X - [Brief Title]`
5. Description: Copy content from `RELEASE_NOTES_vX.X.X.md`
6. Attach files:
   - `PhotoSift.exe`
   - `PhotoSift_Setup.exe`
   - `PhotoSift.msix`
7. Click "Publish release"

## 📦 Step 6: Package Distribution

### 6.1 Desktop Distribution Files
- **Portable**: `PhotoSift.exe` - No installation required
- **Installer**: `PhotoSift_Setup.exe` - Full installation with shortcuts

### 6.2 Microsoft Store Submission
1. Log into Microsoft Partner Center
2. Navigate to PhotoSift app submission
3. Create new submission
4. Upload `PhotoSift.msix`
5. Update store listing (if needed)
6. Submit for certification

### 6.3 Verify Store Package
Before submission, test the MSIX package:
```bash
# Install locally for testing (PowerShell as Admin)
Add-AppxPackage -Path "PhotoSift.msix"

# Verify installation
Get-AppxPackage -Name "PCAI.PhotoSift"

# Test the installed app
# Launch from Start Menu

# Uninstall after testing
Remove-AppxPackage -Package "PCAI.PhotoSift_X.X.X.0_x64__[hash]"
```

## ✅ Step 7: Post-Release Verification

### 7.1 Verification Checklist
- [ ] GitHub release published successfully
- [ ] All package files uploaded and accessible
- [ ] Standalone executable runs without errors
- [ ] Installer creates proper shortcuts and uninstaller
- [ ] MSIX package installs and runs correctly
- [ ] Version numbers consistent across all packages
- [ ] Microsoft Store submission accepted (if applicable)

### 7.2 File Size Verification
Expected approximate sizes:
- `PhotoSift.exe`: ~550MB
- `PhotoSift_Setup.exe`: ~551MB
- `PhotoSift.msix`: ~549MB

### 7.3 Version Verification
Ensure all packages show the correct version:
```bash
# Check executable version (right-click Properties > Details)
# Check installer version (right-click Properties > Details)
# Check MSIX version in AppxManifest.xml
```

## 🚨 Troubleshooting

### Common Build Issues

#### PyInstaller Fails
- Check `version_info.txt` syntax (parentheses matching)
- Verify Python environment activated
- Clear `build/` and `dist/` directories

#### MSIX Creation Fails
- Verify Windows SDK installed
- Check `store_package/AppxManifest.xml` syntax
- Ensure all asset files exist in `Assets/` folder

#### Version Mismatch
- Double-check all version files updated
- Rebuild after version changes
- Verify git tag matches package versions

### Rollback Process
If issues found after release:
1. Do not delete GitHub release (for transparency)
2. Create hotfix version (X.X.X+1)
3. Mark problematic release as "Pre-release" on GitHub
4. Update Microsoft Store with fixed version

## 📊 Release Metrics to Track

- Download counts (GitHub releases)
- Installation success rate
- User feedback and ratings
- Microsoft Store certification time
- Package file sizes and performance

## 🔄 Automated Release (Future Enhancement)

Consider creating GitHub Actions workflow to automate:
- Version number updates
- Package building
- Release creation
- Asset uploading

This would reduce manual steps and ensure consistency across releases.

---

## Quick Reference Commands

### Complete Release Build
```bash
# 1. Update versions in files manually
# 2. Commit version updates
git add setup.py version_info.txt pyproject.toml create_store_package.bat
git commit -m "Bump version to X.X.X"

# 3. Build all packages
.\build.bat
python create_store_assets.py && .\create_store_package.bat && & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift.msix

# 4. Create tag and push
git tag -a vX.X.X -m "Release vX.X.X"
git push origin master
git push origin vX.X.X

# 5. Upload to GitHub releases and Microsoft Store
```

### File Verification
```bash
dir dist\PhotoSift.exe
dir Output\PhotoSift_Setup.exe
dir PhotoSift.msix
git tag --sort=-version:refname
```

---

*Last Updated: October 10, 2025*  
*PhotoSift Release Process v1.1*