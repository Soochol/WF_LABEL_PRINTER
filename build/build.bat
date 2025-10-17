@echo off
REM ============================================
REM WF Label Printer - Build Script
REM Windows 실행 파일 빌드
REM ============================================

echo ======================================
echo WF Label Printer - Build Script
echo ======================================
echo.

REM 프로젝트 루트로 이동
cd ..

REM 1. PyInstaller 설치 확인
echo [1/4] PyInstaller 설치 확인...
python -m pip install --upgrade pip
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: PyInstaller 설치 실패
    pause
    exit /b 1
)
echo.

REM 2. 이전 빌드 결과 정리
echo [2/4] 이전 빌드 결과 정리...
if exist build\WF_Label_Printer rmdir /s /q build\WF_Label_Printer
if exist dist rmdir /s /q dist
echo.

REM 3. PyInstaller 빌드 실행
echo [3/4] PyInstaller 빌드 실행...
pyinstaller build\WF_Label_Printer.spec --clean
if errorlevel 1 (
    echo ERROR: 빌드 실패
    pause
    exit /b 1
)
echo.

REM 4. 배포 패키지 생성
echo [4/4] 배포 패키지 생성...
if not exist build\WF_Label_Printer (
    echo ERROR: 빌드 결과 없음
    pause
    exit /b 1
)

REM data 폴더 생성 (DB 파일이 저장될 위치)
if not exist build\WF_Label_Printer\data mkdir build\WF_Label_Printer\data

REM README 복사
if exist README.md copy README.md build\WF_Label_Printer\
if exist PRINTER_SETUP.md copy PRINTER_SETUP.md build\WF_Label_Printer\

echo.
echo ======================================
echo 빌드 완료!
echo ======================================
echo.
echo 실행 파일 위치: build\WF_Label_Printer\WF_Label_Printer.exe
echo.
echo 배포 시 필요한 파일:
echo   - build\WF_Label_Printer\ 폴더 전체
echo.
pause
