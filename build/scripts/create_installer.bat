@echo off
REM ========================================
REM WF Label Printer - Installer Creation Script
REM Creates installer using Inno Setup
REM ========================================

echo ========================================
echo WF Label Printer - Installer Creation
echo ========================================
echo.

REM Navigate to project root
cd /d "%~dp0..\.."

REM 1. Verify executable exists
echo [1/4] Checking for executable...
if not exist build\application\WF_Label_Printer\WF_Label_Printer.exe (
    echo.
    echo [ERROR] Executable not found!
    echo         Please run build.bat first to create the executable.
    echo.
    exit /b 1
)
echo    - Executable found
echo.

REM 2. Verify prn folder
echo [2/4] Checking prn folder...
if not exist prn (
    echo.
    echo [ERROR] prn folder not found!
    echo.
    exit /b 1
)
echo    - prn folder found
echo.

REM 3. Clean old installers
echo [3/4] Cleaning old installers...
if exist build\installer\*.exe del /q build\installer\*.exe
echo    - Cleanup complete
echo.

REM 4. Run Inno Setup compiler
echo [4/4] Running Inno Setup...
echo    - Script: build\scripts\installer.iss
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build\scripts\installer.iss
if errorlevel 1 (
    echo.
    echo [ERROR] Installer creation failed!
    exit /b 1
)
echo.

REM Display installer file info
for %%I in (build\installer\*.exe) do (
    echo    - Installer: %%~nxI
    echo    - File size: %%~zI bytes
)

echo.
echo ========================================
echo Installer created successfully!
echo ========================================
echo.
