@echo off
REM Build script for PhotoSift with installer

echo Building PhotoSift...

REM Create and activate virtual environment
python -m venv build_env
call build_env\Scripts\activate

REM Install required packages
python -m pip install --upgrade pip
pip install pyinstaller
pip install -e .

REM Build executable with version info
pyinstaller --version-file=version_info.txt PhotoSift.spec

REM Check if Inno Setup is installed
IF EXIST "%PROGRAMFILES(X86)%\Inno Setup 6\ISCC.exe" (
    echo Creating installer...
    "%PROGRAMFILES(X86)%\Inno Setup 6\ISCC.exe" installer.iss
    echo Installer created successfully!
) ELSE (
    echo Inno Setup not found. Please install Inno Setup 6 to create the installer.
    echo Download from: https://jrsoftware.org/isdl.php
)

REM Deactivate virtual environment
deactivate

echo Build complete! Check the dist directory for the executable and Output directory for the installer.
pause