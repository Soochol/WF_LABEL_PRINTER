# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

block_cipher = None

# 프로젝트 루트
project_root = Path.cwd()

# 추가 데이터 파일
# data 폴더는 실행 파일과 같은 위치에 런타임에 생성되므로 포함하지 않음
added_files = [
    (str(project_root / 'prn'), 'prn'),
]

a = Analysis(
    [str(project_root / 'gui_main.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'yaml',
        'usb',
        'usb.core',
        'usb.util',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest-qt',
        'black',
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
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
    name='WF_Label_Printer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 애플리케이션 - 콘솔 창 숨김
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WF_Label_Printer',
)
