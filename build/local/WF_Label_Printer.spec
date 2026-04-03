# -*- mode: python ; coding: utf-8 -*-
"""
WF Label Printer - PyInstaller Spec File (Local Build)
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_all

# PyQt6 전체 수집 (DLL + sip 포함)
qt_datas, qt_binaries, qt_hiddenimports = collect_all('PyQt6')
sip_datas, sip_binaries, sip_hiddenimports = collect_all('PyQt6.sip')
qt_binaries += sip_binaries
qt_hiddenimports += sip_hiddenimports

# 수집할 데이터 파일들
datas = [
    ('../../prns', 'prns'),
] + qt_datas

# Hidden imports
hiddenimports = [
    'pkgutil',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'usb.core',
    'usb.util',
    'usb.backend',
    'usb.backend.libusb1',
    'serial',
    'sqlite3',
]

a = Analysis(
    ['../../main.py'],
    pathex=[str(Path('../..').resolve())],
    binaries=qt_binaries,
    datas=datas,
    hiddenimports=hiddenimports + qt_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WF_Label_Printer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WF_Label_Printer',
)
