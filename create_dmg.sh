#!/bin/bash
# Script per creare DMG di distribuzione per TheNovelist

echo "=========================================="
echo "TheNovelist - DMG Creator"
echo "=========================================="
echo ""

# Check if create-dmg is installed
USE_CREATE_DMG=true
if ! command -v create-dmg &> /dev/null; then
    echo "⚠️  create-dmg non installato, uso metodo fallback"
    echo ""
    USE_CREATE_DMG=false
fi

# Check if app exists
if [ ! -d "dist/TheNovelist.app" ]; then
    echo "❌ dist/TheNovelist.app non trovato"
    echo "Esegui prima: ./build_mac.sh"
    exit 1
fi

# Remove old DMG if exists
rm -f TheNovelist.dmg

echo "📦 Creazione DMG..."
echo ""

if [ "$USE_CREATE_DMG" = true ]; then
    # Create DMG with create-dmg (fancy)
    create-dmg \
      --volname "TheNovelist" \
      --volicon "dist/TheNovelist.app/Contents/Resources/icon.icns" \
      --window-pos 200 120 \
      --window-size 800 400 \
      --icon-size 100 \
      --icon "TheNovelist.app" 200 190 \
      --hide-extension "TheNovelist.app" \
      --app-drop-link 600 185 \
      --no-internet-enable \
      "TheNovelist.dmg" \
      "dist/"

    if [ $? -ne 0 ]; then
        echo "⚠️  create-dmg fallito, uso metodo fallback"
        USE_CREATE_DMG=false
    fi
fi

if [ "$USE_CREATE_DMG" = false ]; then
    # Fallback: create simple DMG manually
    echo "Creazione DMG semplice con hdiutil..."

    # Create temporary directory
    mkdir -p dmg_temp

    # Copy app
    cp -R dist/TheNovelist.app dmg_temp/

    # Create alias to Applications
    ln -s /Applications dmg_temp/Applications

    # Create DMG
    hdiutil create -volname "TheNovelist" -srcfolder dmg_temp -ov -format UDZO TheNovelist.dmg

    # Cleanup
    rm -rf dmg_temp
fi

echo ""
echo "=========================================="
echo "✅ DMG creato con successo!"
echo "=========================================="
echo ""
echo "📦 File: TheNovelist.dmg"
echo "📊 Dimensione: $(du -h TheNovelist.dmg | cut -f1)"
echo ""
echo "Puoi ora distribuire TheNovelist.dmg ai tester Mac"

echo ""
echo "Per testare il DMG:"
echo "  open TheNovelist.dmg"
echo ""
