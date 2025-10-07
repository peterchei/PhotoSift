from setuptools import setup, find_packages

setup(
    name="PhotoSift",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "torch",
        "torchvision",
        "Pillow",
        "numpy",
        "transformers",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "photosift=ImageClassifierGUI:main",
        ],
    },
    author="peterchei",
    description="An AI-powered photo classification and organization tool",
    keywords="photo, classification, AI, machine learning",
)