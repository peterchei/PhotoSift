# PhotoSift

PhotoSift is an AI-powered image classification tool that helps you organize your photos by automatically categorizing them into different types (people photos vs screenshots). It uses the CLIP model from OpenAI for accurate image classification.

## Features

- Drag and drop interface for easy image loading
- Automatic classification of images into categories:
  - People photos (portraits, group photos, selfies, etc.)
  - Screenshots (computer screens, mobile captures, etc.)
- Real-time processing with progress indication
- Easy selection and organization of classified images
- Batch processing capability for large collections
- Simple and intuitive user interface

## System Requirements

- Windows 10/11
- 4GB RAM minimum (8GB recommended)
- Graphics card supporting DirectX 11 or later

## Installation

### Option 1: Using the Installer

1. Download the latest `PhotoSift_Setup.exe` from the releases page
2. Run the installer
3. Follow the installation wizard
4. Launch PhotoSift from the Start Menu or desktop shortcut

### Option 2: Portable Version

1. Download `PhotoSift.exe` from the releases page
2. Run the executable directly (no installation required)

## Building from Source

### Prerequisites

- Python 3.8 or later
- Git
- Inno Setup 6 (optional, for creating installers)

### Build Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/peterchei/PhotoSift.git
   cd PhotoSift
   ```

2. Run the build script:
   ```bash
   .\build.bat
   ```

The build script will:
- Create a virtual environment
- Install required dependencies
- Download necessary AI model files
- Create both standalone executable and installer

### Build Outputs

After a successful build, you'll find:
- Standalone executable in the `dist` folder
- Installer package in the `Output` folder

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Run the application:
   ```bash
   python src/ImageClassifierGUI.py
   ```

## Project Structure

```
PhotoSift/
├── src/
│   ├── ImageClassifierGUI.py    # Main GUI application
│   ├── ImageClassification.py   # AI classification logic
│   └── DuplicateImageIdentifier.py
├── resources/                   # Application resources
├── models/                     # AI model files
├── build.bat                   # Build script
├── setup.py                    # Package configuration
└── README.md                   # Documentation
```

## How It Works

PhotoSift uses the CLIP (Contrastive Language-Image Pre-Training) model from OpenAI to classify images. The model has been trained on a diverse set of images and can effectively distinguish between different types of photos.

The application:
1. Loads images from selected folders
2. Processes them through the CLIP model
3. Classifies them based on confidence scores
4. Organizes them into appropriate categories

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CLIP model by OpenAI
- PyTorch and torchvision teams
- Tkinter for the GUI framework

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/peterchei/PhotoSift/issues) page
2. Create a new issue if your problem isn't already listed
3. Provide as much detail as possible including:
   - Operating System
   - Python version
   - Steps to reproduce the issue