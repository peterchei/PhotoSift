from setuptools import setup, find_packages

setup(
    name="PhotoSift",
    version="1.6.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "torch",
        "torchvision",
        "Pillow",
        "numpy",
        "transformers",
        "opencv-python",
        "tqdm",  # Used by transformers for progress bars
        "requests",  # Used by transformers for downloading models
        "packaging",  # Used by transformers for version handling
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "photosift=launchPhotoSiftApp:main",
        ],
    },
    author="peterchei",
    description="An AI-powered photo classification and organization tool",
    keywords="photo, classification, AI, machine learning",
)