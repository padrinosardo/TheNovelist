#!/bin/bash
# Build script for TheNovelist - Linux

echo "=========================================="
echo "TheNovelist - Linux Build Script"
echo "=========================================="
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found!"
    exit 1
fi
echo ""

# Step 2: Clean previous builds
echo "Step 2: Cleaning previous builds..."
rm -rf build/ dist/
echo ""

# Step 3: Build with PyInstaller
echo "Step 3: Building application with PyInstaller..."
pyinstaller TheNovelist.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Build successful!"
    echo "=========================================="
    echo ""
    echo "Application: dist/TheNovelist/TheNovelist"
    echo ""
    ls -lh dist/TheNovelist/TheNovelist
    echo ""
else
    echo ""
    echo "=========================================="
    echo "Build failed!"
    echo "=========================================="
    exit 1
fi
