# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['combined_gui_mac.py'],
    pathex=[],
    binaries=[],
    datas=[('sounds/', 'sounds'), ('kuromi.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Liberty County Tools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['kuromi.png'],
)
app = BUNDLE(
    exe,
    name='Liberty County Tools.app',
    icon='kuromi.png',
    bundle_identifier=None,
)
