create-dmg \
    --volname "Liberty County Tools Installer" \
    --background background.png \
    --window-pos 200 120 \
    --window-size 1000 800 \
    "dist/Liberty County Tools Installer.dmg" \
    "dist/Liberty County Tools DMG"

# make writable
# hdiutil convert "Liberty County Tools Installer.dmg" -format UDRW -o "Liberty County Tools Writable.dmg"

# convert it back to UDZO