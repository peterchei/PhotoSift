# Microsoft Store Package Checklist

## Version 1.2.0 - Package Preparation Guide

This checklist ensures your PhotoSift MSIX package passes all Microsoft Store validation checks.

---

## ✅ Pre-Build Checklist

### 1. Version Numbers Updated
- [ ] `setup.py` - version="1.2.0"
- [ ] `pyproject.toml` - version = "1.2.0"
- [ ] `version_info.txt` - filevers=(1, 2, 0, 0) and prodvers=(1, 2, 0, 0)
- [ ] `create_store_package.bat` - Version="1.2.0.0"
- [ ] `installer.iss` - MyAppVersion "1.2.0"

### 2. Build Environment Ready
- [ ] Python environment activated
- [ ] All dependencies installed
- [ ] PyInstaller available
- [ ] Windows SDK installed (for makeappx.exe)

---

## 🔧 Build Process

### Step 1: Build Desktop Executable
```powershell
.\build.bat
```

**Verify:**
- [ ] `dist\PhotoSift.exe` exists (~550MB)
- [ ] `Output\PhotoSift_Setup.exe` exists (~551MB)
- [ ] No build errors in output

### Step 2: Create Store Assets
```powershell
python create_store_assets.py
```

**Verify Required Assets Created:**
- [ ] `store_package\Assets\Square44x44Logo.png` (44x44px, ~2-3 KB)
- [ ] `store_package\Assets\Square150x150Logo.png` (150x150px, ~15 KB)
- [ ] `store_package\Assets\StoreLogo.png` (50x50px, ~3 KB)

**Optional Assets (Recommended):**
- [ ] `store_package\Assets\Square71x71Logo.png` (71x71px)
- [ ] `store_package\Assets\Square310x310Logo.png` (310x310px)

**Asset Quality Check:**
- [ ] All PNGs have transparent background (RGBA mode)
- [ ] Icons are centered with proper padding
- [ ] Icons are clear and recognizable at all sizes
- [ ] File sizes are reasonable (<100KB each)

### Step 3: Create Package Structure
```powershell
.\create_store_package.bat
```

**Verify Package Structure:**
- [ ] `store_package\PhotoSift.exe` copied
- [ ] `store_package\app.ico` copied
- [ ] `store_package\Assets\` folder with all logos
- [ ] `store_package\AppxManifest.xml` created

### Step 4: Validate AppxManifest.xml

**Critical Elements Check:**

```xml
<!-- Identity -->
<Identity Name="PCAI.PhotoSift" 
          Publisher="CN=3DE80B9A-18CE-447E-8E83-D1237B056E60" 
          Version="1.2.0.0" />

<!-- Properties -->
<Properties>
  <DisplayName>PhotoSift</DisplayName>
  <PublisherDisplayName>PC@AI</PublisherDisplayName>
  <Logo>Assets\Square150x150Logo.png</Logo>
</Properties>

<!-- CRITICAL: Language Support -->
<Resources>
  <Resource Language="en-us" />
</Resources>

<!-- Visual Elements -->
<uap:VisualElements 
  DisplayName="PhotoSift" 
  Description="AI-powered photo organization tool" 
  Square150x150Logo="Assets\Square150x150Logo.png" 
  Square44x44Logo="Assets\Square44x44Logo.png" 
  BackgroundColor="transparent">
</uap:VisualElements>
```

**Validation Checklist:**
- [ ] Identity Name matches reserved app name
- [ ] Publisher matches developer certificate
- [ ] Version is X.X.X.0 format (four components)
- [ ] PublisherDisplayName is "PC@AI" (matches Partner Center)
- [ ] Resources section includes `<Resource Language="en-us" />`
- [ ] All logo paths match actual file locations
- [ ] Description is present and descriptive
- [ ] Capabilities include `<rescap:Capability Name="runFullTrust" />`

### Step 5: Create MSIX Package
```powershell
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift.msix
```

**Verify:**
- [ ] `PhotoSift.msix` created (~580-620 MB)
- [ ] No errors in makeappx output
- [ ] "Package creation succeeded" message displayed

---

## 🔍 Common Validation Errors & Fixes

### Error 1: Missing Logo Assets
**Error Message:**
```
Package acceptance validation error: The following image(s) specified in the appxManifest.xml 
were not found: Assets\Square150x150Logo.png, Assets\Square44x44Logo.png
```

**Fix:**
1. Run `python create_store_assets.py`
2. Verify files exist in `store_package\Assets\`
3. Check AppxManifest.xml paths match exactly (case-sensitive)

### Error 2: PublisherDisplayName Mismatch
**Error Message:**
```
Package acceptance validation error: The PublisherDisplayName element in the app manifest 
is , which doesn't match your publisher display name: PC@AI.
```

**Fix:**
1. Open `store_package\AppxManifest.xml`
2. Verify `<PublisherDisplayName>PC@AI</PublisherDisplayName>` (no extra spaces)
3. Update `create_store_package.bat` to include correct publisher name
4. Rebuild package

### Error 3: Missing Language Support
**Error Message:**
```
Package acceptance validation error: The package must declare support for at least one language.
Package acceptance validation error: The package specifies an unsupported default language:
```

**Fix:**
1. Open `store_package\AppxManifest.xml`
2. Add after `</Properties>` and before `<Dependencies>`:
```xml
<Resources>
  <Resource Language="en-us" />
</Resources>
```
3. Update `create_store_package.bat` to include Resources section
4. Rebuild package

### Error 4: Package Identity Mismatch
**Error Message:**
```
Package acceptance validation error: The package identity name does not match the reserved name.
```

**Fix:**
1. Verify Identity Name in AppxManifest matches Partner Center reservation
2. Should be: `PCAI.PhotoSift`
3. Publisher should be: `CN=3DE80B9A-18CE-447E-8E83-D1237B056E60`

---

## 📋 Pre-Submission Final Checklist

### Package Validation
- [ ] MSIX file size is reasonable (580-620 MB expected)
- [ ] Package creation completed without errors
- [ ] All assets referenced in manifest exist in package

### Local Testing (Optional)
```powershell
# Enable Developer Mode first (Settings > Update & Security > For Developers)
Add-AppxPackage -Path PhotoSift.msix

# Test the installed app
# Launch from Start Menu

# Uninstall after testing
Get-AppxPackage *PhotoSift* | Remove-AppxPackage
```

- [ ] Package installs successfully (with Developer Mode)
- [ ] App launches without errors
- [ ] Main features work correctly
- [ ] App appears in Start Menu with correct icon

### Documentation Ready
- [ ] `RELEASE_NOTES_v1.2.0.md` created
- [ ] Screenshots prepared (3-8 recommended)
- [ ] Privacy policy updated (if needed)
- [ ] Support contact information ready

### Partner Center Preparation
- [ ] Microsoft Partner Center account active
- [ ] App name "PhotoSift" reserved
- [ ] Publisher display name set to "PC@AI"
- [ ] Age rating questionnaire completed
- [ ] Pricing tier determined (Free recommended)

---

## 🚀 Submission Steps

1. **Login to Partner Center**
   - Go to https://partner.microsoft.com/dashboard
   - Navigate to Windows apps

2. **Create New Submission**
   - Select PhotoSift app
   - Click "Start new submission"

3. **Upload Package**
   - Navigate to Packages section
   - Upload `PhotoSift.msix`
   - Wait for validation (1-5 minutes)
   - ✅ All checks should pass

4. **Complete Store Listing**
   - Description: Use prepared text from `RELEASE_NOTES_v1.2.0.md`
   - Screenshots: Upload 3-8 PNG images
   - Categories: "Photo & Video" or "Utilities & tools"
   - Keywords: photo organizer, duplicate finder, AI photo manager

5. **Submit for Certification**
   - Review all sections
   - Click "Submit to the Store"
   - Wait for certification (1-7 business days)

---

## 📝 Post-Submission Tracking

### Certification Status
- [ ] Submission received confirmation
- [ ] In certification (check daily)
- [ ] Approved/Rejected notification received
- [ ] If approved: App live in Store
- [ ] If rejected: Review feedback and fix issues

### Version History
- Version 1.0.0: Initial release
- Version 1.1.0: Dark theme and UI improvements
- **Version 1.2.0: Enhanced duplicate finder, tooltips, improved UX** ← Current

---

## 🛠️ Quick Fix Reference

### Rebuild Package from Scratch
```powershell
# Clean up
Remove-Item -Recurse -Force store_package -ErrorAction SilentlyContinue
Remove-Item PhotoSift.msix -ErrorAction SilentlyContinue

# Rebuild everything
.\build.bat
python create_store_assets.py
.\create_store_package.bat
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift.msix
```

### Verify Package Contents
```powershell
# List package contents
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" unpack /p PhotoSift.msix /d temp_unpack

# Check manifest
type temp_unpack\AppxManifest.xml

# Clean up
Remove-Item -Recurse -Force temp_unpack
```

---

## 📞 Support Resources

- **Microsoft Store Policies**: https://docs.microsoft.com/windows/uwp/publish/store-policies
- **MSIX Documentation**: https://docs.microsoft.com/windows/msix/
- **Partner Center Help**: https://docs.microsoft.com/windows/uwp/publish/
- **PhotoSift GitHub**: https://github.com/peterchei/PhotoSift

---

**Last Updated:** October 12, 2025  
**Package Version:** 1.2.0  
**Status:** ✅ Ready for Submission
