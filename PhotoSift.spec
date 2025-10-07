# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/ImageClassifierGUI.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/*.py', '.'),  # Include all Python files
        ('models/clip-vit-base-patch32/*', 'models/clip-vit-base-patch32/'),  # Include CLIP model files
    ],
    hiddenimports=[
        'PIL',
        'torch', 
        'torchvision',
        'numpy',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'transformers',
        'transformers.models.clip',
        'transformers.models.clip.modeling_clip',
        'transformers.models.clip.processing_clip'
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