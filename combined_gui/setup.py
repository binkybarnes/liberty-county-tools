from cx_Freeze import setup, Executable
import sys
import os

# Include sound files
include_files = [("sounds", "sounds")]

# Setup options
options = {
    "build_exe": {
        "packages": ["pygame"],
        "include_files": include_files,
    }
}

# Set base for Windows (hides the console window)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Executable configuration
setup(
    name="LibertyCountySuite",
    version="1.0",
    description="atm, lockpick",
    options=options,
    executables=[Executable("combined_gui.py", base=base)]
)
