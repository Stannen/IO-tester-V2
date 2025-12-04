#!/bin/bash
set -e

ENTRY="main.py"
APPNAME="mijn_app"
DIST_DIR="release"

# Lijsten met folders en bestanden die je wilt bundelen
EXTRA_DIRS=("defauld/config" "defauld/export" "defauld/saved_progress")
ADD_DATA_ITEMS=("defauld:defauld")

# Optioneel: tesseract binaries en modellen
TESSERACT_BIN="/usr/bin/tesseract"
TESSDATA_DIR="/usr/share/tesseract-ocr/4.00/tessdata"

echo ">>> Opruimen oude build..."
rm -rf build dist __pycache__ *.spec "$DIST_DIR"

# Bouw de --add-data argumenten dynamisch
ADD_DATA_ARGS=""
for item in "${ADD_DATA_ITEMS[@]}"; do
    ADD_DATA_ARGS="$ADD_DATA_ARGS --add-data $item"
done

echo ">>> Bouwen met PyInstaller..."
eval python3 -m PyInstaller --onefile \
    --name "$APPNAME" \
    $ADD_DATA_ARGS \
    "$ENTRY"

echo ">>> Aanmaken distributiemap $DIST_DIR..."
mkdir -p "$DIST_DIR"

echo ">>> Kopiëren executable..."
cp "dist/$APPNAME" "$DIST_DIR/"

echo ">>> Kopiëren extra folders (inhoud)..."
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

