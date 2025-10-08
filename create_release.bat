@echo off
setlocal enabledelayedexpansion

REM Get version from user
set /p VERSION="Enter release version (e.g., 1.0.0): "

REM Create and push git tag
git tag -a v%VERSION% -m "Release version %VERSION%"
git push origin v%VERSION%

REM Run the build script
call build.bat

REM Calculate checksums
echo Calculating checksums...
echo SHA-256 Checksums: > checksums.txt
certutil -hashfile "dist\PhotoSift.exe" SHA256 >> checksums.txt
certutil -hashfile "Output\PhotoSift_Setup.exe" SHA256 >> checksums.txt

echo.
echo Release v%VERSION% has been tagged and built.
echo.
echo Next steps:
echo 1. Go to https://github.com/peterchei/PhotoSift/releases/new
echo 2. Choose tag v%VERSION%
echo 3. Upload files from:
echo    - Output\PhotoSift_Setup.exe
echo    - dist\PhotoSift.exe
echo 4. Copy checksums from checksums.txt
echo.
echo Press any key to view the checksums...
pause >nul
type checksums.txt
pause