@echo off
REM ========================================
REM WF Label Printer - Build Script
REM Builds executable using PyInstaller
REM ========================================

echo ========================================
echo WF Label Printer - Build Process
echo ========================================
echo.

REM Navigate to project root
cd /d "%~dp0..\.."

REM ========================================
REM STEP 1: Clean previous build
REM ========================================
echo [1/4] Cleaning previous build...
if exist build\application rmdir /s /q build\application
if exist build\temp rmdir /s /q build\temp
echo    - Cleanup complete
echo.

REM ========================================
REM STEP 2: Verify virtual environment
REM ========================================
echo [2/4] Checking virtual environment...
if not exist .venv\Scripts\python.exe (
    echo.
    echo [ERROR] Virtual environment not found!
    echo         Please create venv first: python -m venv .venv
    echo.
    exit /b 1
)
echo    - Virtual environment found
echo.

REM ========================================
REM STEP 3: Verify PyInstaller
REM ========================================
echo [3/4] Verifying PyInstaller installation...
.venv\Scripts\python.exe -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo.
    echo [WARNING] PyInstaller not found. Installing...
    .venv\Scripts\python.exe -m pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller!
        exit /b 1
    )
)
echo    - PyInstaller ready
echo.

REM ========================================
REM STEP 4: Build executable
REM ========================================
echo [4/4] Building executable...
echo    - Spec file: build\scripts\build_app.spec
echo    - Output: build\application\
echo.

.venv\Scripts\pyinstaller.exe ^
    --distpath build\application ^
    --workpath build\temp ^
    --clean ^
    build\scripts\build_app.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Output location: build\application\WF_Label_Printer\
echo.
