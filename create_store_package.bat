@echo off
setlocal enabledelayedexpansion

echo Creating MSIX package for Microsoft Store...

REM Ensure the store package directory exists
if not exist "store_package" mkdir store_package

REM Run the build first to ensure we have the latest executable
call build.bat

REM Copy required files to the package directory
xcopy /y "dist\PhotoSift.exe" "store_package\"
xcopy /y "resources\app.ico" "store_package\"

REM Create store assets
python create_store_assets.py

REM Create the AppxManifest.xml
echo ^<?xml version="1.0" encoding="utf-8"?^> > "store_package\AppxManifest.xml"
echo ^<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10" >> "store_package\AppxManifest.xml"
echo         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10" >> "store_package\AppxManifest.xml"
echo         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"^> >> "store_package\AppxManifest.xml"
echo   ^<Identity Name="PCAI.PhotoSift" >> "store_package\AppxManifest.xml"
echo            Publisher="CN=3DE80B9A-18CE-447E-8E83-D1237B056E60" >> "store_package\AppxManifest.xml"
echo            Version="1.2.0.0" /^> >> "store_package\AppxManifest.xml"
echo   ^<Properties^> >> "store_package\AppxManifest.xml"
echo     ^<DisplayName^>PhotoSift^</DisplayName^> >> "store_package\AppxManifest.xml"
echo     ^<PublisherDisplayName^>PC@AI^</PublisherDisplayName^> >> "store_package\AppxManifest.xml"
echo     ^<Logo^>Assets\Square150x150Logo.png^</Logo^> >> "store_package\AppxManifest.xml"
echo   ^</Properties^> >> "store_package\AppxManifest.xml"
echo   ^<Resources^> >> "store_package\AppxManifest.xml"
echo     ^<Resource Language="en-us" /^> >> "store_package\AppxManifest.xml"
echo   ^</Resources^> >> "store_package\AppxManifest.xml"
echo   ^<Dependencies^> >> "store_package\AppxManifest.xml"
echo     ^<TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.19041.0"/^> >> "store_package\AppxManifest.xml"
echo   ^</Dependencies^> >> "store_package\AppxManifest.xml"
echo   ^<Capabilities^> >> "store_package\AppxManifest.xml"
echo     ^<rescap:Capability Name="runFullTrust" /^> >> "store_package\AppxManifest.xml"
echo   ^</Capabilities^> >> "store_package\AppxManifest.xml"
echo   ^<Applications^> >> "store_package\AppxManifest.xml"
echo     ^<Application Id="PhotoSift" >> "store_package\AppxManifest.xml"
echo                  Executable="PhotoSift.exe" >> "store_package\AppxManifest.xml"
echo                  EntryPoint="Windows.FullTrustApplication"^> >> "store_package\AppxManifest.xml"
echo       ^<uap:VisualElements DisplayName="PhotoSift" >> "store_package\AppxManifest.xml"
echo                            Description="AI-powered photo organization tool" >> "store_package\AppxManifest.xml"
echo                            Square150x150Logo="Assets\Square150x150Logo.png" >> "store_package\AppxManifest.xml"
echo                            Square44x44Logo="Assets\Square44x44Logo.png" >> "store_package\AppxManifest.xml"
echo                            BackgroundColor="transparent"^> >> "store_package\AppxManifest.xml"
echo       ^</uap:VisualElements^> >> "store_package\AppxManifest.xml"
echo     ^</Application^> >> "store_package\AppxManifest.xml"
echo   ^</Applications^> >> "store_package\AppxManifest.xml"
echo ^</Package^> >> "store_package\AppxManifest.xml"

echo Package prepared in store_package directory.
echo.
echo Next steps for Microsoft Store submission:
echo 1. Install Windows SDK (if not already installed)
echo 2. Use MakeAppx.exe tool to create the MSIX package:
echo    makeappx pack /d store_package /p PhotoSift.msix
echo.
echo 3. Sign the package with your certificate:
echo    signtool sign /fd SHA256 /a /f your_cert.pfx PhotoSift.msix
echo.
echo 4. Test the package locally:
echo    Add-AppxPackage -Path PhotoSift.msix
echo.
echo 5. Submit to Partner Center:
echo    https://partner.microsoft.com/dashboard/windows/overview
echo.
pause