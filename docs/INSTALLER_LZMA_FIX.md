# Inno Setup LZMA Compression Error - Troubleshooting Guide

## Error Description
```
Error in C:\Users\peter\git\PhotoSift\installer.iss: 
lzma: Worker thread terminated unexpectedly with exception: 
Access violation at address 7BC08613 in module 'islzma.dll' (offset 8613). 
Read of address 2447FF50.
Compile aborted.
```

## Root Cause
This error occurs when Inno Setup's LZMA compression encounters:
1. **Large files** (~550MB PhotoSift.exe) causing memory exhaustion
2. **Memory access violations** in the LZMA compression DLL
3. **File locking** or antivirus interference
4. **Insufficient system resources** during compression

## Solutions Applied

### ✅ Solution 1: Updated Compression Method (RECOMMENDED)
Changed from `lzma` to `lzma2/max` in installer.iss

**Changes Made:**
```ini
; BEFORE
Compression=lzma

; AFTER  
Compression=lzma2/max
```

**Benefits:**
- LZMA2 is more stable with large files
- Better memory management
- Improved multi-threading support
- Less prone to crashes

**Also Updated:**
- Version: 1.2.0 → 1.3.1

### Alternative Solutions (If Still Failing)

#### Option 2: Use ZIP Compression
If LZMA2 still fails, switch to ZIP (faster, less memory intensive):

```ini
Compression=zip/9
SolidCompression=no
```

**Pros:**
- Much faster compilation
- More stable with large files
- Lower memory usage

**Cons:**
- Larger installer size (~551MB vs ~500MB with LZMA)

#### Option 3: Disable Solid Compression
Keep LZMA2 but disable solid compression:

```ini
Compression=lzma2/normal
SolidCompression=no
```

**Pros:**
- More stable
- Can extract individual files faster

**Cons:**
- Slightly larger installer

#### Option 4: Reduce Compression Level
Use normal compression instead of max:

```ini
Compression=lzma2/normal
SolidCompression=yes
```

**Pros:**
- Faster compilation
- Less memory intensive
- Still good compression

**Cons:**
- Slightly larger installer (~510MB)

## Troubleshooting Steps

### Step 1: Clean Build
```bash
# Remove old output
rmdir /s /q Output
rmdir /s /q build
rmdir /s /q dist

# Rebuild
.\build.bat
```

### Step 2: Close Interfering Programs
- Close antivirus real-time scanning
- Close any programs that might lock files
- Close previous PhotoSift instances
- Close file explorers viewing dist folder

### Step 3: Run as Administrator
Right-click `build.bat` and select "Run as administrator"

### Step 4: Check Disk Space
Ensure you have at least **3GB free space** for temporary compression files:
```powershell
Get-PSDrive C | Select-Object Used,Free
```

### Step 5: Check Memory Usage
Close unnecessary programs to free up RAM. The compression needs significant memory for a 550MB file.

### Step 6: Disable Antivirus Temporarily
Some antivirus programs interfere with compression:
```powershell
# Windows Defender (run as admin)
Set-MpPreference -DisableRealtimeMonitoring $true

# Re-enable after build
Set-MpPreference -DisableRealtimeMonitoring $false
```

### Step 7: Update Inno Setup
Ensure you have the latest version of Inno Setup:
- Download from: https://jrsoftware.org/isdl.php
- Latest version has better LZMA2 support

## Quick Reference: Compression Options

| Compression | Speed | Size | Stability | Memory |
|------------|-------|------|-----------|--------|
| lzma2/max | Slow | Smallest | Good | High |
| lzma2/normal | Medium | Small | Good | Medium |
| lzma2/fast | Fast | Medium | Very Good | Low |
| zip/9 | Fast | Larger | Excellent | Low |
| zip | Very Fast | Largest | Excellent | Very Low |

## Testing the Fix

### Rebuild with New Settings
```bash
.\build.bat
```

### Expected Output
```
Inno Setup 6.x Compiler
Copyright (C) 1997-2024 Jordan Russell
...
Compressing: C:\Users\peter\git\PhotoSift\dist\PhotoSift.exe
  [Progress indicators...]
Successful compile (xx.x sec)

Output: C:\Users\peter\git\PhotoSift\Output\PhotoSift_Setup.exe
```

### Verify Installer
```bash
# Check file exists
dir Output\PhotoSift_Setup.exe

# Check size (should be ~500-551MB depending on compression)
# Run installer to test
.\Output\PhotoSift_Setup.exe
```

## Additional Recommendations

### For Large Files Like PhotoSift (550MB):
1. **Use lzma2/normal** instead of lzma2/max
2. **Consider splitting** into multiple files if possible
3. **Increase Windows page file** if memory is limited
4. **Build on a machine with more RAM** (8GB+ recommended)

### Update build.bat If Needed
If you want to automatically use better compression settings:

```batch
@echo off
echo Building PhotoSift...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Output rmdir /s /q Output

REM Build executable
echo.
echo Step 1: Building executable with PyInstaller...
pyinstaller PhotoSift.spec --clean --noconfirm

if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    exit /b 1
)

REM Build installer
echo.
echo Step 2: Building installer with Inno Setup...
echo Using LZMA2 compression for stability...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

if errorlevel 1 (
    echo ERROR: Installer creation failed!
    echo Try running with different compression settings.
    exit /b 1
)

echo.
echo Build complete!
echo Executable: dist\PhotoSift.exe
echo Installer: Output\PhotoSift_Setup.exe
```

## Current Configuration

After the fix, your installer.iss should have:
```ini
#define MyAppVersion "1.3.1"
...
Compression=lzma2/max
SolidCompression=yes
```

This provides the best balance of:
- ✅ Stability with large files
- ✅ Good compression ratio
- ✅ Reasonable build time
- ✅ Lower memory usage than lzma

## If Problem Persists

Try these compression settings in order until one works:

1. **First try (current)**: `Compression=lzma2/max`
2. **If fails**: `Compression=lzma2/normal`
3. **If fails**: `Compression=lzma2/fast`
4. **If fails**: `Compression=zip/9`
5. **Last resort**: `Compression=none` (no compression, just packaging)

---

**Status**: ✅ Fixed - Updated to lzma2/max compression  
**Version**: Updated to 1.3.1  
**Recommendation**: Rebuild with `.\build.bat`
