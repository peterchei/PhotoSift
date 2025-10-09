# Microsoft Store Submission Guide

## Prerequisites

1. **Developer Account**
   - Register at [Microsoft Partner Center](https://partner.microsoft.com/dashboard/registration)
   - One-time registration fee: $19 (individual account)
   - Complete identity verification process

2. **Required Tools**
   - [MSIX Packaging Tool](https://www.microsoft.com/store/productId/9N5LW3JBCXKF) from Microsoft Store
   - Optional: Visual Studio (recommended for development)

## Package Preparation

### Option 1: Automated Package Creation (Recommended)

1. **Run the Store Package Script**
   ```powershell
   # This script handles everything: build, assets, and package structure
   .\create_store_package.bat
   ```
   This script will:
   - Build the latest PhotoSift.exe using PyInstaller
   - Copy required files to store_package directory
   - Generate proper AppxManifest.xml with correct settings
   - Display next steps for creating MSIX package

2. **Generate Store Assets**
   ```powershell
   # Generate required store assets from app icon
   python create_store_assets.py
   ```
   This will create all required store assets from your app icon:
   - Square44x44Logo.png (44x44)
   - Square150x150Logo.png (150x150)

3. **Create MSIX Package**
   ```powershell
   # Create MSIX package using Windows SDK
   & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" pack /d store_package /p PhotoSift.msix
   ```
   This creates a PhotoSift.msix file ready for store submission.

### Option 2: Using MSIX Packaging Tool (Alternative)

   A. **Install MSIX Packaging Tool**
   - Download and install the [MSIX Packaging Tool](https://apps.microsoft.com/store/detail/msix-packaging-tool/9N5LW3JBCXKF) from the Microsoft Store
   - Run the tool as administrator

   B. **Create Package**
   1. Open MSIX Packaging Tool
   2. Select "Application Package" from the main menu
   3. Choose "Create package for Microsoft Store"
   4. In the package information:
      - Package name: PhotoSift
      - Package display name: PhotoSift
      - Publisher display name: Your publisher name
   5. For the installer:
      - Select "Executable package (.exe)"
      - Browse to `dist\PhotoSift.exe`
   6. For assets:
      - Use the existing assets in `store_package\Assets`
      - The tool will automatically include:
        - Square44x44Logo.png (app list icon)
        - Square150x150Logo.png (medium tile)

   C. **Validate and Create Package**
   1. Review the package settings
   2. Choose "Create" to generate the package
   3. The tool will create a signed MSIX package ready for store submission

   D. **Test the Package (Optional)**
   ```powershell
   # Enable Developer Mode in Windows Settings first
   Add-AppxPackage -Register .\store_package\AppxManifest.xml
   ```

   > Note: The MSIX Packaging Tool handles signing automatically for store submission. When testing locally, Developer Mode allows running unsigned packages.

## Package Testing (Optional)

Before submitting to the store, you can test your MSIX package locally:

1. **Enable Developer Mode**
   - Go to Windows Settings > Update & Security > For developers
   - Enable "Developer mode"

2. **Install Package Locally**
   ```powershell
   # Install the MSIX package for testing
   Add-AppxPackage -Path PhotoSift.msix
   ```

3. **Test Application**
   - Launch PhotoSift from Start Menu
   - Verify all functionality works correctly
   - Test with sample images

4. **Uninstall Test Package** (when ready to submit)
   ```powershell
   # Remove test installation
   Get-AppxPackage *PhotoSift* | Remove-AppxPackage
   ```

## Store Submission Steps

### 1. Prepare Package Information
Before submitting, ensure you have:
- PhotoSift.msix package (ready for upload)
- App description and features list
- Screenshots of the application (recommended: 3-8 screenshots)
- Privacy policy URL (if app handles user data)
- Support contact information

### 2. Submit to Microsoft Store
1. Go to [Partner Center](https://partner.microsoft.com/dashboard)
2. Sign in with your developer account
3. Create a new app submission
4. **App Identity**: Reserve app name "PhotoSift"
5. **Packages**: Upload PhotoSift.msix
6. **Store Listings**: Fill in required information:
   - **App name**: PhotoSift
   - **Description**: AI-powered photo organization tool that automatically sorts your images into categories like people, screenshots, documents, and more using advanced machine learning.
   - **Category**: Utilities & Tools
   - **Subcategory**: File managers
   - **Pricing**: Free (or set your price)
   - **Age ratings**: Fill out questionnaire (likely General audiences)
7. **Properties**: Set availability and device family support
8. **Submissions**: Review and submit for certification

### 3. Certification Process
- Microsoft will review your app (typically 1-7 days)
- You'll receive email notifications about the status
- If approved, your app will be available in the Microsoft Store
- If rejected, you'll receive feedback and can resubmit after fixing issues

## Required Assets

### Store Listing Graphics
The required store assets are generated automatically by the `create_store_assets.py` script and will be used by the MSIX Packaging Tool:

- **Required App Logos** (generated automatically in store_package/Assets)
  - Square44x44Logo.png: 44x44 px (app list icon)
  - Square150x150Logo.png: 150x150 px (medium tile)

These assets are automatically generated by the `create_store_assets.py` script and included in the package structure.

### Package Contents
Your final MSIX package will contain:
- **PhotoSift.exe** (~576 MB) - Main application executable
- **AppxManifest.xml** - Package manifest with app metadata
- **Assets/** - Directory containing store logos
  - Square44x44Logo.png (app list icon)
  - Square150x150Logo.png (medium tile)
  - StoreLogo.png (store listing logo)
- **app.ico** - Application icon file

### Screenshots
- Minimum: 1 screenshot
- Recommended: 3-8 screenshots
- Resolution: 1920x1080 px (landscape)
- Format: PNG or JPEG
- Suggestions for PhotoSift:
  1. Main interface with images loaded
  2. Classification process in action
  3. Sorted results showing people photos
  4. Sorted results showing screenshots
  5. Settings or preferences panel

### Feature Graphic
- Size: 2400x1200 px
- Format: PNG or JPEG

## Troubleshooting

### Common Issues and Solutions

1. **Build Failures**
   - Ensure all dependencies are installed in the virtual environment
   - Check that PyInstaller completes without errors
   - Verify PhotoSift.exe is created in the dist directory

2. **MSIX Package Creation Fails**
   - Verify Windows SDK is installed and makeappx.exe is available
   - Check that all required files exist in store_package directory
   - Ensure AppxManifest.xml is valid

3. **Package Installation Fails (Testing)**
   - Enable Developer Mode in Windows Settings
   - Check Windows Event Viewer for detailed error messages
   - Verify package manifest has correct capabilities

4. **Store Submission Rejected**
   - Review Microsoft's feedback carefully
   - Common issues: missing privacy policy, inappropriate content ratings
   - Update package and resubmit

### Support Resources
- [Microsoft Store App Developer Agreement](https://docs.microsoft.com/legal/windows/agreements/app-developer-agreement)
- [Microsoft Store Policies](https://docs.microsoft.com/windows/uwp/publish/store-policies)
- [MSIX Packaging Documentation](https://docs.microsoft.com/windows/msix/)
- [Partner Center Help](https://docs.microsoft.com/windows/uwp/publish/)
- Must represent app's core features
- Suggested design for PhotoSift:
  - Split view showing before/after organization
  - AI classification visualization
  - Clean, modern design highlighting efficiency

## Store Submission Process

1. **Access Partner Center**
   - Go to [Partner Center Dashboard](https://partner.microsoft.com/dashboard)
   - Select 'Create a new app'

2. **Product Setup**
   - Product type: Application
   - Name reservation: "PhotoSift"
   - Category: 
     - Primary: Photo & Video
     - Secondary: Productivity

3. **Properties**
   - Privacy Policy URL
   - Support contact info
   - Website link: https://github.com/peterchei/PhotoSift

4. **Store Listing**
   - Description (Sample):
     ```
     PhotoSift is an AI-powered image organization tool that automatically categorizes your photos using advanced machine learning technology. Perfect for photographers, social media managers, and anyone looking to organize their photo collection efficiently.

     Key Features:
     • AI-powered image classification
     • Automatic sorting of people photos and screenshots
     • Drag and drop interface
     • Batch processing capability
     • Real-time classification feedback
     • Easy file management
     • Modern, user-friendly interface

     Save hours of manual sorting and keep your photo collection organized automatically with PhotoSift.
     ```
   - Search terms: photo organizer, image sorter, AI photo tool, picture organization
   - Screenshots (as described above)
   - App logos
   - Feature graphic

5. **Technical Configuration**
   - Upload MSIX package
   - System Requirements:
     - Windows 10 version 17763.0 or higher
     - 4GB RAM minimum
     - DirectX 11 compatible graphics
   - Capabilities:
     - File system access
     - Pictures library access

6. **Pricing and Availability**
   - Price: Free
   - Markets: All markets
   - Release: Immediate
   - Visibility: Public

7. **Age Ratings**
   - Expected rating: ESRB EVERYONE
   - No offensive content
   - No real-time communication
   - No user data collection beyond basic app functionality

## Testing

1. **Local Testing**
   ```powershell
   # Install package locally
   Add-AppxPackage -Path PhotoSift.msix
   ```

2. **Validation Testing**
   - Run Windows App Certification Kit
   - Test on various Windows versions
   - Verify all features:
     - Image loading
     - Classification
     - UI responsiveness
     - File operations

## Submission Checklist

- [ ] Developer account active
- [ ] MSIX package created and signed
- [ ] App logos created (all sizes)
- [ ] Screenshots prepared
- [ ] Feature graphic designed
- [ ] Privacy policy published
- [ ] Support contact info ready
- [ ] Age rating questionnaire completed
- [ ] Local testing completed
- [ ] Package validated with certification kit

## Resources

- [Partner Center](https://partner.microsoft.com/dashboard)
- [Windows SDK Documentation](https://docs.microsoft.com/windows/win32)
- [Store Submission Guidelines](https://docs.microsoft.com/windows/uwp/publish)
- [MSIX Documentation](https://docs.microsoft.com/windows/msix)

## Support

For additional help:
- Microsoft Store Support: [Partner Center Support](https://partner.microsoft.com/support)
- Developer Community: [Windows Developer Community](https://docs.microsoft.com/windows/apps)
- PhotoSift Issues: [GitHub Issues](https://github.com/peterchei/PhotoSift/issues)

## Notes

Remember to:
1. Test the MSIX package thoroughly before submission
2. Prepare all graphics assets in advance
3. Write clear, engaging store descriptions
4. Set up proper support channels
5. Monitor the submission process in Partner Center
6. Respond quickly to any certification feedback