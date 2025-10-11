# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/launchPhotoSiftApp.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/*.py', '.'),  # Include all Python files
        ('models/clip-vit-base-patch32/*', 'models/clip-vit-base-patch32/'),  # Include CLIP model files
        ('models/*', 'models/'),  # Include any other model files
    ],
    hiddenimports=[
        # Image and graphics libraries
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'cv2',
        'opencv-python',
        
        # AI/ML libraries  
        'torch', 
        'torchvision',
        'numpy',
        'transformers',
        'transformers.models',
        'transformers.models.clip',
        'transformers.models.clip.modeling_clip',
        'transformers.models.clip.processing_clip',
        'transformers.models.clip.configuration_clip',
        'transformers.models.clip.image_processing_clip',
        'transformers.models.clip.tokenization_clip',
        'transformers.models.clip.tokenization_clip_fast',
        'transformers.image_processing_utils',
        'transformers.tokenization_utils',
        'transformers.tokenization_utils_base',
        'transformers.configuration_utils',
        'transformers.modeling_utils',
        'transformers.processing_utils',
        'transformers.utils',
        
        # GUI libraries
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        
        # Threading and async
        'concurrent.futures',
        'threading',
        'multiprocessing',
        'queue',
        
        # File system and data handling
        'pathlib',
        'glob',
        'shutil',
        'json',
        'pickle',
        'zipfile',
        'tarfile',
        
        # Standard library modules
        'math',
        'time',
        'sys',
        'os',
        'collections',
        'itertools',
        'functools',
        'operator',
        'warnings',
        'typing',
        'dataclasses',
        
        # PyTorch specific modules that might be missed
        'torch.nn',
        'torch.nn.functional',
        'torch.utils',
        'torch.utils.data',
        'torchvision.transforms',
        
        # HuggingFace transformers additional modules
        'transformers.generation',
        'transformers.trainer_utils',
        'transformers.file_utils',
        'transformers.activations',
        
        # PhotoSift modules (ensure all local modules are included)
        'ImageClassification',
        'ImageClassifierGUI', 
        'DuplicateImageIdentifier',
        'DuplicateImageIdentifierGUI',
        'CommonUI',
        'launchPhotoSiftApp'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PhotoSift',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app.ico',
    version='version_info.txt'
)