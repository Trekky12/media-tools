#!/bin/bash

APP_NAME="HEIC-Convert"
DESKTOP="Schreibtisch"

EXECUTABLE_SRC="$(pwd)/heic-convert"
EXECUTABLE_DIR="$HOME/.local/bin"
EXECUTABLE_TARGET="$EXECUTABLE_DIR/$APP_NAME"

ICON_SRC="$(pwd)/images-regular-full.svg"
ICON_DIR="$HOME/.local/share/icons"
ICON_TARGET="$ICON_DIR/$APP_NAME.svg"

DESKTOP_FILE="$HOME/.local/share/applications/$APP_NAME.desktop"

mkdir -p "$EXECUTABLE_DIR"
mkdir -p "$ICON_DIR"

cp "$EXECUTABLE_SRC" "$EXECUTABLE_TARGET"
chmod +x "$EXECUTABLE_TARGET"

cp "$ICON_SRC" "$ICON_TARGET"

cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Name=$APP_NAME
Exec=$EXECUTABLE_TARGET
Icon=$ICON_TARGET
Terminal=false
Type=Application
Categories=Utility
StartupWMClass=Heic-convert
EOL

chmod +x "$DESKTOP_FILE"

cp "$DESKTOP_FILE" "$HOME/$DESKTOP/$APP_NAME.desktop"

echo "Desktop shortcut created"
