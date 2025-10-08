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

1. **Generate Store Assets**
   ```powershell
   # Generate required store assets from app icon
   python create_store_assets.py
   ```
   This will create all required store assets from your app icon:
   - Square44x44Logo (44x44)
   - Square150x150Logo (150x150)

2. **Create Store Package using MSIX Packaging Tool**

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

## Store Submission Steps

1. Go to [Partner Center](https://partner.microsoft.com/dashboard)
2. Create a new app submission
3. Upload the generated .msix package
4. Fill in required store listing information:
   - App name
   - Description
   - Category: Utilities & Tools
   - Pricing
   - Age ratings
5. Submit for certification

## Required Assets

### Store Listing Graphics
The required store assets are generated automatically by the `create_store_assets.py` script and will be used by the MSIX Packaging Tool:

- **Required App Logos** (generated automatically in store_package/Assets)
  - Square44x44Logo.png: 44x44 px (app list icon)
  - Square150x150Logo.png: 150x150 px (medium tile)

These assets will be automatically detected and used by the MSIX Packaging Tool when creating your store package.

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