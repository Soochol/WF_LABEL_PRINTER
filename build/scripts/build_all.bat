@echo off
REM ========================================
REM WF Label Printer - Complete Build Script
REM Builds executable + installer in one go
REM ========================================

echo ========================================
echo WF Label Printer - Complete Build
echo ========================================
echo.
echo This script will:
echo   1. Build executable (PyInstaller)
echo   2. Create installer (Inno Setup)
echo.
echo ========================================
echo.

REM Navigate to project root
cd /d "%~dp0..\.."

REM ========================================
REM STEP 1: Build executable
REM ========================================
echo.
echo ========================================
echo STEP 1: Building Executable
echo ========================================
echo.

call build\scripts\build.bat
if errorlevel 1 (
    echo.
    echo [ERROR] Executable build failed!
    exit /b 1
)

REM ========================================
REM STEP 2: Create installer
REM ========================================
echo.
echo ========================================
echo STEP 2: Creating Installer
echo ========================================
echo.

call build\scripts\create_installer.bat
if errorlevel 1 (
    echo.
    echo [ERROR] Installer creation failed!
    exit /b 1
)

REM ========================================
REM Complete
REM ========================================
echo.
echo ========================================
echo All builds completed successfully!
echo ========================================
echo.
echo Generated files:
echo   - Executable: build\application\WF_Label_Printer\WF_Label_Printer.exe
echo   - Installer:  build\installer\WF_Label_Printer_Setup_v1.0.0.exe
echo.
