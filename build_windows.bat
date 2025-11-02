@echo off
REM Build script for Windows

echo ==========================================
echo TheNovelist - Windows Build Script
echo ==========================================
echo.

REM Check if running on Windows
if not "%OS%"=="Windows_NT" (
    echo Error: This script is for Windows only
    exit /b 1
)

REM Step 1: Check Python version
echo Step 1: Checking Python version...
python --version
echo.

REM Step 2: Check if virtual environment exists
echo Step 2: Checking virtual environment...
if not exist "venv\" (
    echo    Creating virtual environment...
    python -m venv venv
)
echo    Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Step 3: Install/upgrade dependencies
echo Step 3: Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
echo.

REM Step 4: Download spaCy model if not present
echo Step 4: Checking spaCy Italian model...
python -c "import spacy; spacy.load('it_core_news_sm')" 2>nul
if errorlevel 1 (
    echo    Downloading Italian spaCy model...
    python -m spacy download it_core_news_sm
) else (
    echo    Italian spaCy model already installed
)
echo.

REM Step 5: Clean previous builds
echo Step 5: Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
echo    Cleaned
echo.

REM Step 6: Run PyInstaller
echo Step 6: Building application...
pyinstaller TheNovelist.spec

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo Build successful!
    echo ==========================================
    echo.
    echo Application folder: dist\TheNovelist\
    echo.
    echo To test the application:
    echo   dist\TheNovelist\TheNovelist.exe
    echo.
    echo To create an installer for distribution:
    echo   1. Install Inno Setup from https://jrsoftware.org/isdl.php
    echo   2. Create an installer script or use a tool like NSIS
    echo.
) else (
    echo.
    echo ==========================================
    echo Build failed!
    echo ==========================================
    exit /b 1
)

pause
