@echo off
REM ============================================
REM WF Label Printer - Local Build Script
REM Build Windows EXE using PyInstaller
REM ============================================

echo ======================================
echo WF Label Printer - Local Build
echo ======================================
echo.

REM Spec file paths are relative to build\local\, so run PyInstaller from there
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%~dp0..\..

REM 1. Check uv
echo [1/4] Checking uv...
where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv not found. Install from https://docs.astral.sh/uv/
    pause
    exit /b 1
)
uv --version
echo.

REM 2. Install PyInstaller via uv (run from project root where pyproject.toml is)
echo [2/4] Installing PyInstaller...
pushd "%PROJECT_ROOT%"
uv add pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    popd
    pause
    exit /b 1
)
popd
echo.

REM 3. Clean previous build
echo [3/4] Cleaning previous build...
if exist "%SCRIPT_DIR%dist" rmdir /s /q "%SCRIPT_DIR%dist"
echo    - Done
echo.

REM 4. Run PyInstaller from build\local\ so spec relative paths resolve correctly
echo [4/4] Running PyInstaller...
pushd "%SCRIPT_DIR%"
uv run python -m PyInstaller WF_Label_Printer.spec --clean
if errorlevel 1 (
    echo ERROR: Build failed
    popd
    pause
    exit /b 1
)
popd

echo.
echo ======================================
echo Build complete!
echo ======================================
echo.
echo Output: %SCRIPT_DIR%dist\WF_Label_Printer\WF_Label_Printer.exe
echo.
pause
