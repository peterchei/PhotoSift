@echo on
setlocal enabledelayedexpansion

echo Building PhotoSift...

REM Clean up previous build artifacts
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Create and activate virtual environment
if not exist build_env (
    python -m venv build_env
)
call build_env\Scripts\activate

REM Install required packages
python -m pip install --upgrade pip
pip install pyinstaller
pip install -e .

REM Ensure the icon exists
if not exist "resources\app.ico" (
    echo Creating icon...
    python create_icon.py
)

REM Build executable with PyInstaller
echo Building executable with PyInstaller...
pyinstaller PhotoSift.spec
if not exist "dist\PhotoSift.exe" (
    echo ERROR: PyInstaller failed to create the executable.
    echo Please check the output above for error messages.
    pause
    exit /b 1
)

REM Check if Inno Setup is installed
IF EXIST "%PROGRAMFILES(X86)%\Inno Setup 6\ISCC.exe" (
    echo Creating installer...
    "%PROGRAMFILES(X86)%\Inno Setup 6\ISCC.exe" installer.iss
    if errorlevel 1 (
        echo ERROR: Inno Setup failed to create the installer.
        pause
        exit /b 1
    )
    echo Installer created successfully!
) ELSE (
    echo Inno Setup not found. Please install Inno Setup 6 to create the installer.
    echo Download from: https://jrsoftware.org/isdl.php
)

REM Deactivate virtual environment
deactivate

echo Build complete! Check the dist directory for the executable and Output directory for the installer.
pause