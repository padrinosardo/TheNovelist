# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for TheNovelist
Supports both macOS and Windows builds
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all spaCy data files and models
spacy_datas = collect_data_files('spacy', include_py_files=True)
spacy_hiddenimports = collect_submodules('spacy')

# Collect spaCy Italian model
try:
    it_model_datas = collect_data_files('it_core_news_sm', include_py_files=True)
except:
    print("WARNING: it_core_news_sm not found. Install with: python -m spacy download it_core_news_sm")
    it_model_datas = []

# Collect language-tool-python data
language_tool_datas = collect_data_files('language_tool_python')

# Add custom resources
added_files = [
    ('resources', 'resources'),  # Include all templates and resources
]

# Combine all data files
datas = added_files + spacy_datas + it_model_datas + language_tool_datas

# Hidden imports needed by the application
hiddenimports = [
    'spacy',
    'it_core_news_sm',
    'language_tool_python',
    'anthropic',
    'markdown',
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'docx',
    'docx.enum',
    'docx.shared',
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtPrintSupport',
] + spacy_hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'pandas',
        'scipy',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TheNovelist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TheNovelist',
)

# macOS specific: Create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='TheNovelist.app',
        bundle_identifier='com.thenovelist.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'CFBundleName': 'TheNovelist',
            'CFBundleDisplayName': 'TheNovelist',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHumanReadableCopyright': 'Copyright © 2024',
        },
    )
