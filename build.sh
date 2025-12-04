#!/bin/bash
# build.sh - Maak een standalone distributie met PyInstaller en extra folders

set -e  # stop bij fouten

# Configuratie
ENTRY="main.py"
APPNAME="mijn_app"
#CONFIG="default_config.yaml"
DIST_DIR="release"   # uiteindelijke distributiemap
EXTRA_DIRS=("saved_progress" "config" "export")
TESSERACT_BIN="/usr/bin/tesseract"        # pad naar tesseract binary in WSL
TESSDATA_DIR="/usr/share/tesseract-ocr/4.00/tessdata"  # taalmodellen

echo ">>> Opruimen oude build..."
rm -rf build dist __pycache__ *.spec "$DIST_DIR"

echo ">>> Bouwen met PyInstaller..."
python3 -m PyInstaller --onefile \
    --name "$APPNAME" \
    --add-data "$CONFIG:." \
    "$ENTRY"

echo ">>> Aanmaken distributiemap $DIST_DIR..."
mkdir -p "$DIST_DIR"

echo ">>> Kopiëren executable..."
cp "dist/$APPNAME" "$DIST_DIR/"

echo ">>> Kopiëren extra folders..."
for d in "${EXTRA_DIRS[@]}"; do
    if [ -d "$d" ]; then
        cp -r "$d" "$DIST_DIR/"
    else
        echo "Waarschuwing: folder $d bestaat niet, overslaan."
    fi
done

echo ">>> Kopiëren Tesseract binaries..."
mkdir -p "$DIST_DIR/tesseract"
cp "$TESSERACT_BIN" "$DIST_DIR/tesseract/"
cp -r "$TESSDATA_DIR" "$DIST_DIR/tesseract/"

echo ">>> Klaar! Alles staat in $DIST_DIR/"

