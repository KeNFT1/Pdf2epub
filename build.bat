@echo off
REM PDF to ePub Converter - Windows Build Script
REM This script creates a standalone .exe file for Windows distribution

echo ====================================
echo PDF to ePub Converter Build Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv build_env

echo Activating virtual environment...
call build_env\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Building executable with PyInstaller...
echo This may take a few minutes...

REM Create the executable
pyinstaller --onefile --windowed --name "PDF2ePub-Converter" --icon=app.ico main.py

REM Check if build was successful
if exist "dist\PDF2ePub-Converter.exe" (
    echo.
    echo ====================================
    echo BUILD SUCCESSFUL!
    echo ====================================
    echo.
    echo Executable created: dist\PDF2ePub-Converter.exe
    echo File size: 
    dir "dist\PDF2ePub-Converter.exe" | find "PDF2ePub-Converter.exe"
    echo.
    echo You can now distribute the .exe file to any Windows computer.
    echo No Python installation required on target machines.
    echo.
) else (
    echo.
    echo ====================================
    echo BUILD FAILED!
    echo ====================================
    echo.
    echo Check the build output above for errors.
    echo.
)

echo Deactivating virtual environment...
call deactivate

echo.
echo Cleaning up build files...
rmdir /s /q build 2>nul
del /q PDF2ePub-Converter.spec 2>nul

echo.
echo Build process completed.
pause