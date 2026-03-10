# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for RobotAtlas.

Usage (from ia-clases/ directory, inside activated venv):
    pyinstaller ../installer/robotatlas.spec

Output: ia-clases/dist/RobotAtlas/  (one-folder bundle)
"""

import os
import sys
from pathlib import Path

# ---------- paths ----------------------------------------------------------
# This spec is invoked from ia-clases/, so '.' is ia-clases/
SRC_DIR = os.path.abspath('.')
INSTALLER_DIR = os.path.dirname(os.path.abspath(SPECPATH))

# ---------- runtime hook for UTF-8 console ---------------------------------
runtime_hooks = [os.path.join(INSTALLER_DIR, 'pyi_rth_utf8.py')]

# ---------- hidden imports -------------------------------------------------
# Application modules (subprocess-based classes import these at runtime)
app_hiddenimports = [
    'paths',
    'class_manager',
    'class_progress_manager',
    'class_progress_reporter',
    'class_student_loader',
    'class_demo_manager',
    'demo_sequence_manager',
    'student_sync_manager',
    'mrl_connector',
    'demo_player',
    'sequence_esp32_logger',
    # modules package
    'modules',
    'modules.camera',
    'modules.class_config',
    'modules.config',
    'modules.esp32',
    'modules.qr',
    'modules.questions',
    'modules.slides',
    'modules.speech',
    'modules.utils',
    # services package
    'services',
    'services.esp32_services',
    'services.esp32_services.esp32_client',
    'services.esp32_services.esp32_config',
    'services.esp32_services.esp32_config_binary',
    'services.esp32_services.esp32_connector',
    # tabs package
    'tabs',
    'tabs.base_tab',
    'tabs.main_tab',
    'tabs.esp32_tab',
    'tabs.sequence_builder_tab',
    'tabs.settings_tab',
    'tabs.simulator_tab',
    'tabs.class_builder_tab',
    'tabs.class_controller_tab',
    'tabs.mobile_app_tab',
    'tabs.students_manager_tab',
    'tabs.demo_sequence_tab',
    'tabs.classes_manager_tab',
    'tabs.class_progress_widget',
    # config package
    'config',
    'config.settings',
]

# Third-party libraries that PyInstaller commonly misses
lib_hiddenimports = [
    # TTS
    'pyttsx3',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'pyttsx3.drivers.dummy',
    # Speech / audio
    'speech_recognition',
    'sounddevice',
    'pyaudio',
    # Vision
    'cv2',
    'mediapipe',
    'mediapipe.python',
    'mediapipe.python.solutions',
    'face_recognition',
    'face_recognition_models',
    'dlib',
    # Image / PDF
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'fitz',
    'pymupdf',
    # Scientific / math
    'numpy',
    'scipy',
    'scipy.spatial',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'ikpy',
    'ikpy.chain',
    'ikpy.link',
    # AI / API
    'openai',
    'httpx',
    'httpcore',
    'pydantic',
    # Networking
    'requests',
    'bs4',
    # Environment
    'dotenv',
    'python_dotenv',
    # OCR
    'pytesseract',
    # Utils
    'tqdm',
    'colorama',
    'pygame',
    # Windows-specific
    'comtypes',
    'win32com',
    'win32com.client',
    # Tkinter
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    # Stdlib (sometimes missed in frozen builds)
    'http.server',
    'urllib.parse',
    'json',
    'threading',
    'socket',
    'collections',
    'typing',
]

hiddenimports = app_hiddenimports + lib_hiddenimports

# ---------- data files (read-only bundled resources) -----------------------
datas = [
    # Class definitions & metadata
    ('clases', 'clases'),
    # Config module
    ('config', 'config'),
    # Default config / seed files
    ('env.example', '.'),
    ('esp32_config.json', '.'),
    ('students_data.json', '.'),
    # Demo configurations
    ('demos', 'demos'),
    # Saved sequences
    ('sequences', 'sequences'),
]

# Conditionally add directories/files that may not exist
optional_datas = [
    ('esp32_config.bin', '.'),
]
for src, dst in optional_datas:
    if os.path.exists(os.path.join(SRC_DIR, src)):
        datas.append((src, dst))

# ---------- analysis -------------------------------------------------------
a = Analysis(
    ['robot_gui_conmodulos.py'],
    pathex=[SRC_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks,
    excludes=[
        # Exclude heavy packages we don't use
        'torch',
        'tensorflow',
        'transformers',
        'IPython',
        'notebook',
        'jupyter',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RobotAtlas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            # GUI application — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RobotAtlas',
)
