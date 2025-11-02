#!/bin/bash
# Build script for macOS

echo "=========================================="
echo "TheNovelist - macOS Build Script"
echo "=========================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is for macOS only"
    exit 1
fi

# Step 1: Check Python version
echo "📋 Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $PYTHON_VERSION"
echo ""

# Step 2: Check if virtual environment exists
echo "📋 Step 2: Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi
echo "   Activating virtual environment..."
source venv/bin/activate
echo ""

# Step 3: Install/upgrade dependencies
echo "📋 Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
echo ""

# Step 4: Download spaCy model if not present
echo "📋 Step 4: Checking spaCy Italian model..."
python3 -c "import spacy; spacy.load('it_core_news_sm')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "   Downloading Italian spaCy model..."
    python3 -m spacy download it_core_news_sm
else
    echo "   ✓ Italian spaCy model already installed"
fi
echo ""

# Step 5: Clean previous builds
echo "📋 Step 5: Cleaning previous builds..."
rm -rf build/ dist/ TheNovelist.app
echo "   ✓ Cleaned"
echo ""

# Step 6: Run PyInstaller
echo "📋 Step 6: Building application..."
pyinstaller TheNovelist.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Build successful!"
    echo "=========================================="
    echo ""
    echo "📦 Application bundle: dist/TheNovelist.app"
    echo ""
    echo "To test the application:"
    echo "  open dist/TheNovelist.app"
    echo ""
    echo "To create a DMG for distribution:"
    echo "  1. Install create-dmg: brew install create-dmg"
    echo "  2. Run: create-dmg --volname 'TheNovelist' --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon 'TheNovelist.app' 200 190 --hide-extension 'TheNovelist.app' --app-drop-link 600 185 'TheNovelist.dmg' 'dist/'"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Build failed!"
    echo "=========================================="
    exit 1
fi
