create-dmg \
    --volname "Liberty County Tools Installer" \
    --background background.png \
    --window-pos 200 120 \
    --window-size 1000 800 \
    "dist/Liberty County Tools Installer.dmg" \
    "dist/Liberty County Tools DMG"

# make writable
# hdiutil convert "Liberty County Tools Installer.dmg" -format UDRW -o "Liberty County Tools Writable.dmg"
# pyinstaller --onefile --windowed --icon=kuromi.png --add-data "sound/:sound" --add-data "kuromi.png:." --name "Liberty County Tools" combined_gui_mac.py
