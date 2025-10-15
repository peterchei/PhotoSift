# PhotoSift v1.3.0 Release Checklist

## Pre-Release Checklist

### Code Quality
- [x] All regression tests passing (33/33)
- [x] No syntax errors
- [x] Module imports working correctly
- [x] Unicode path fix tested and verified
- [x] Threshold feature tested and working
- [x] Start scan button implemented
- [x] Auto-select groups working

### Version Updates
- [x] `setup.py` updated to v1.3.0
- [x] `version_info.txt` updated to v1.3.0 (FileVersion and ProductVersion)
- [x] `CHANGELOG.md` created with full history
- [x] `RELEASE_NOTES_v1.3.0.md` created

### Documentation
- [x] `UNICODE_PATH_FIX.md` - Technical details of Unicode fix
- [x] `THRESHOLD_ENHANCEMENT.md` - Threshold feature guide
- [x] `START_SCAN_BUTTON_ENHANCEMENT.md` - Workflow improvements
- [x] `AUTO_SELECT_GROUPS_FEATURE.md` - Auto-select implementation
- [ ] README.md updated with v1.3.0 features (if needed)

### Build Process
- [ ] Run `build.bat` successfully
- [ ] Test the built executable
- [ ] Verify installer creation
- [ ] Test installer on clean system

### Git Repository
- [ ] Commit all changes
- [ ] Create git tag v1.3.0
- [ ] Push commits to master
- [ ] Push tags to remote

## Release Steps

### 1. Final Build
```batch
# Run build script (includes cleaning and building)
build.bat

# Verify output
dir dist\PhotoSift.exe
```

### 1a. (Optional) Create Microsoft Store Package
```batch
# Create MSIX package for MS Store
create_store_package.bat

# This will:
# - Run build.bat
# - Create store assets with v1.3.0
# - Generate AppxManifest.xml with version 1.3.0.0
# - Prepare store_package directory
```

### 2. Test the Build
```powershell
# Run the executable
.\dist\PhotoSift.exe

# Test all three tools:
# - Blur Detection
# - Duplicate Detection (test with Unicode path)
# - Image Classification

# Verify:
# - All features work
# - No crashes
# - Unicode paths work correctly
# - Threshold slider functions
# - Start scan button works
# - Auto-select groups works
```

### 3. Git Commit and Tag
```powershell
# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "Release v1.3.0: Unicode support, threshold control, and UX improvements

Major changes:
- Fixed critical Unicode path bug affecting international users
- Added adjustable similarity threshold (80%-99%) for duplicate detection
- Added Start Scan button for better workflow control
- Added auto-select groups for immediate result display
- Comprehensive documentation and testing

Full changelog in CHANGELOG.md"

# Create annotated tag
git tag -a v1.3.0 -m "PhotoSift v1.3.0

Major Release: Unicode Support and Enhanced User Control

Key Features:
- Unicode path support for international users
- Adjustable similarity threshold with fast re-grouping
- Improved scanning workflow with Start Scan button
- Auto-select groups for instant result display

Bug Fixes:
- Fixed critical Unicode path handling issue
- Resolved false duplicate detection for non-English paths

See RELEASE_NOTES_v1.3.0.md for detailed release notes."

# Push to remote
git push origin master
git push origin v1.3.0
```

### 4. Create GitHub Release

Go to: https://github.com/peterchei/PhotoSift/releases/new

**Tag**: v1.3.0
**Release Title**: PhotoSift v1.3.0 - Unicode Support & Enhanced Control
**Description**: Copy from `RELEASE_NOTES_v1.3.0.md`

**Assets to upload**:
- `PhotoSift.exe` (standalone executable)
- `PhotoSift-1.3.0-Setup.exe` (installer, if created)

### 5. Post-Release
- [ ] Verify release is visible on GitHub
- [ ] Test download links
- [ ] Update any external documentation
- [ ] Announce release (if applicable)

## Testing Instructions for Users

### For New Users
1. Download PhotoSift v1.3.0
2. Run installer or extract executable
3. Test all three tools with your images
4. Pay special attention to folders with Unicode characters

### For Upgrading Users
1. Download v1.3.0
2. Run installer (will upgrade automatically)
3. **Important**: Re-scan folders that previously showed false duplicates
4. Test the new threshold slider in Duplicate Detection
5. Enjoy the improved workflow!

### Test Scenarios

#### Unicode Path Testing
```
Test folder: E:\Peter's Photo\22-03-2002 華山派聚會
Expected: Images should have realistic similarity scores (not all 100%)
```

#### Threshold Testing
```
1. Scan a folder for duplicates
2. Adjust threshold from 95% to 80%
3. Click "Re-group with New Threshold"
4. Verify: Fast re-grouping (10-20x faster than initial scan)
5. Verify: More groups appear with lower threshold
```

#### Start Scan Button
```
1. Click "Select Folder"
2. Verify: Image count displayed
3. Verify: Scan button enabled
4. Adjust threshold (optional)
5. Click "Start Scan"
6. Verify: Scan begins with selected threshold
```

#### Auto-Select Groups
```
1. Complete a duplicate scan
2. Verify: All groups automatically selected in tree view
3. Verify: Images displayed immediately
4. Change threshold and re-group
5. Verify: Groups auto-selected again
```

## Rollback Plan

If critical issues are found:

1. Remove v1.3.0 release from GitHub
2. Create hotfix branch
3. Fix issues
4. Release v1.3.1 with fixes
5. Update CHANGELOG.md

## Notes

- Version 1.3.0 is a significant release with major bug fixes
- Unicode support is critical for international users
- All features are backward compatible
- No breaking changes in this release
- Thoroughly tested with 33 regression tests

## Success Criteria

- [ ] Build completes without errors
- [ ] All tests pass
- [ ] Executable runs on Windows 10/11
- [ ] Unicode paths work correctly
- [ ] New features function as documented
- [ ] No regression in existing features
- [ ] GitHub release created successfully
- [ ] Documentation is complete and accurate
