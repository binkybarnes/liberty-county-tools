create-dmg \
    --volname "Liberty County Tools Installer" \
    --background background.png \
    --window-pos 200 120 \
    --window-size 1400 800 \
    "dist/Liberty County Tools Installer.dmg" \
    "dist/Liberty County Tools DMG"

# make writable
hdiutil convert "dist/Liberty County Tools Installer.dmg" -format UDRW -o "dist/Liberty County Tools Writable.dmg"
# make read only
# hdiutil convert "dist/Liberty County Tools Writable.dmg" -format UDZO -o "dist/Liberty County Tools.dmg"


# create app
# pyinstaller --onefile --windowed --icon=kuromi.png --add-data "sounds/:sounds" --add-data "kuromi.png:." --name "Liberty County Tools" combined_gui_mac.py
