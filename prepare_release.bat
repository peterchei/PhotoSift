@echo off
REM PhotoSift v1.3.0 Release Preparation Script
REM This script automates the release preparation process

echo ================================================================
echo PhotoSift v1.3.0 Release Preparation
echo ================================================================
echo.

REM Check if we're in the right directory
if not exist "setup.py" (
    echo ERROR: setup.py not found. Please run this script from the PhotoSift root directory.
    exit /b 1
)

echo [1/6] Running regression tests...
echo ----------------------------------------------------------------
cd tests
python run_all_tests.pypython.exe -m pip install --upgrade pippython.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo ERROR: Tests failed! Please fix failing tests before releasing.
    cd ..
    exit /b 1
)
cd ..
echo.
echo ✓ All tests passed!
echo.

echo [2/6] Checking Python syntax...
echo ----------------------------------------------------------------
python -m py_compile src\DuplicateImageIdentifier.py
if errorlevel 1 (
    echo ERROR: Syntax error in DuplicateImageIdentifier.py
    exit /b 1
)
python -m py_compile src\DuplicateImageIdentifierGUI.py
if errorlevel 1 (
    echo ERROR: Syntax error in DuplicateImageIdentifierGUI.py
    exit /b 1
)
python -m py_compile src\ImageClassification.py
if errorlevel 1 (
    echo ERROR: Syntax error in ImageClassification.py
    exit /b 1
)
python -m py_compile src\ImageClassifierGUI.py
if errorlevel 1 (
    echo ERROR: Syntax error in ImageClassifierGUI.py
    exit /b 1
)
python -m py_compile src\BlurryImageDetection.py
if errorlevel 1 (
    echo ERROR: Syntax error in BlurryImageDetection.py
    exit /b 1
)
python -m py_compile src\BlurryImageDetectionGUI.py
if errorlevel 1 (
    echo ERROR: Syntax error in BlurryImageDetectionGUI.py
    exit /b 1
)
python -m py_compile src\CommonUI.py
if errorlevel 1 (
    echo ERROR: Syntax error in CommonUI.py
    exit /b 1
)
python -m py_compile src\launchPhotoSiftApp.py
if errorlevel 1 (
    echo ERROR: Syntax error in launchPhotoSiftApp.py
    exit /b 1
)
echo.
echo ✓ All Python files have valid syntax!
echo.

echo [3/6] Cleaning previous builds...
echo ----------------------------------------------------------------
if exist "dist" (
    rmdir /s /q dist
    echo ✓ Removed dist directory
)
if exist "build" (
    rmdir /s /q build
    echo ✓ Removed build directory
)
if exist "PhotoSift.spec" (
    del PhotoSift.spec
    echo ✓ Removed old spec file
)
echo.

echo [4/6] Building executable...
echo ----------------------------------------------------------------
call build.bat
if errorlevel 1 (
    echo.
    echo ERROR: Build failed! Check the error messages above.
    exit /b 1
)
echo.
echo ✓ Build completed successfully!
echo.

echo [5/6] Verifying build output...
echo ----------------------------------------------------------------
if not exist "dist\PhotoSift.exe" (
    echo ERROR: PhotoSift.exe not found in dist directory!
    exit /b 1
)

REM Check file size (should be > 100MB due to PyTorch and models)
for %%A in (dist\PhotoSift.exe) do set size=%%~zA
if %size% LSS 10000000 (
    echo WARNING: PhotoSift.exe seems too small (%size% bytes)
    echo This might indicate a packaging issue.
)

echo ✓ PhotoSift.exe found in dist directory
echo   Size: %size% bytes
echo.

echo [6/6] Checking version consistency...
echo ----------------------------------------------------------------
findstr /C:"version=\"1.3.0\"" setup.py >nul
if errorlevel 1 (
    echo ERROR: setup.py does not have version 1.3.0
    exit /b 1
)
echo ✓ setup.py: version 1.3.0

findstr /C:"filevers=(1, 3, 0, 0)" version_info.txt >nul
if errorlevel 1 (
    echo ERROR: version_info.txt does not have filevers 1.3.0
    exit /b 1
)
echo ✓ version_info.txt: filevers 1.3.0

findstr /C:"FileVersion\", u\"1.3.0\"" version_info.txt >nul
if errorlevel 1 (
    echo ERROR: version_info.txt does not have FileVersion 1.3.0
    exit /b 1
)
echo ✓ version_info.txt: FileVersion 1.3.0

echo.
echo ================================================================
echo Release Preparation Complete!
echo ================================================================
echo.
echo Next steps:
echo   1. Test the executable: dist\PhotoSift.exe
echo   2. Verify all features work correctly
echo   3. Test with Unicode folder paths
echo   4. Review RELEASE_CHECKLIST_v1.3.0.md
echo   5. Commit changes and create git tag
echo   6. Push to GitHub and create release
echo.
echo Git commands:
echo   git add .
echo   git commit -m "Release v1.3.0"
echo   git tag -a v1.3.0 -m "PhotoSift v1.3.0 Release"
echo   git push origin master
echo   git push origin v1.3.0
echo.
echo ================================================================

pause
