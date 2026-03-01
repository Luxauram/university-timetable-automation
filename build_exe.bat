@echo off
:: ============================================================================
:: build_exe.bat
:: Builds a standalone Windows executable using PyInstaller.
::
:: Requirements:
::   - Python 3.10+ installed and available in PATH
::   - icon.ico in the same directory (optional, 256x256 ICO format)
::
:: Output: dist\University_Timetable_Automation.exe
:: ============================================================================

echo.
echo ============================================
echo  University Timetable Automation - Build EXE
echo ============================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Make sure Python and pip are in your PATH.
    pause
    exit /b 1
)

echo.
echo [2/3] Compiling executable...

if exist icon.ico (
    set ICON_FLAG=--icon icon.ico
) else (
    echo WARNING: icon.ico not found. Building without icon.
    set ICON_FLAG=
)

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "University_Timetable_Automation" ^
    --collect-all pypdfium2 ^
    %ICON_FLAG% ^
    main.py

if %errorlevel% neq 0 (
    echo ERROR: PyInstaller compilation failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Done! Executable created at:
echo  dist\University_Timetable_Automation.exe
echo ============================================
echo.
pause
