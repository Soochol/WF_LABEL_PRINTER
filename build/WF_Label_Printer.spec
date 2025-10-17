# -*- mode: python ; coding: utf-8 -*-
"""
WF Label Printer - PyInstaller Spec File
Windows 실행 파일 빌드 설정
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로
project_root = Path.cwd()

# 수집할 데이터 파일들
datas = [
    ('../templates', 'templates'),  # PRN 템플릿 파일들
]

# Hidden imports (동적 import 되는 모듈들)
hiddenimports = [
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

# 분석 단계
a = Analysis(
    ['../gui_main.py'],  # build 폴더에서 실행되므로 상위 디렉토리 참조
    pathex=[str(Path('..').resolve())],  # 프로젝트 루트를 경로에 추가
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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

# PYZ 아카이브
pyz = PYZ(a.pure)

# 실행 파일 생성
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
    console=False,  # GUI 앱이므로 콘솔 창 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일이 있다면 경로 지정
)

# 배포 폴더 생성 (build/WF_Label_Printer에 생성)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WF_Label_Printer',
)

# 빌드 후 처리: dist/WF_Label_Printer -> build/WF_Label_Printer로 이동
import shutil
from pathlib import Path

dist_path = Path('dist/WF_Label_Printer')
build_output = Path('build/WF_Label_Printer')

if dist_path.exists():
    # 기존 build/WF_Label_Printer 삭제 (있다면)
    if build_output.exists():
        shutil.rmtree(build_output)

    # build 폴더가 없으면 생성
    build_output.parent.mkdir(parents=True, exist_ok=True)

    # dist -> build로 이동
    shutil.move(str(dist_path), str(build_output))

    print(f"\n========================================")
    print(f"빌드 완료!")
    print(f"========================================")
    print(f"실행 파일: {build_output / 'WF_Label_Printer.exe'}")
    print(f"배포 폴더: {build_output}")
    print(f"========================================\n")

