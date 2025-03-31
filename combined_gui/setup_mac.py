from setuptools import setup
import sys

sys.setrecursionlimit(5000)

APP = ["combined_gui_mac.py"]
DATA_FILES = ["sounds", "kuromi.png"]
PLIST = {
    "CFBundleName": "Liberty County Tools",  # The app title
    "CFBundleDisplayName": "Liberty County Tools",
    "CFBundleIdentifier": "com.binkybarnes.libertycountytools",
    "CFBundleIconFile": "kuromi.png",  # The app icon
}

setup(
    app=APP,
    data_files=[(dir, [file]) for dir, file in zip(DATA_FILES, DATA_FILES)],
    options={
        "py2app": {
            "argv_emulation": True,
            "iconfile": "kuromi.png",
        }
    },
    setup_requires=["py2app"],
    plist=PLIST,
)
