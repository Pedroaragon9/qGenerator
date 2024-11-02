# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Qgen.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    name='Qgenerator',
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
    icon=['/Users/Pedarf/Desktop/Python scripts/qGenerator/250px_arwing_starlink_6XL_icon.ico'],
)
app = BUNDLE(
    exe,
    name='Qgenerator.app',
    icon='/Users/Pedarf/Desktop/Python scripts/qGenerator/250px_arwing_starlink_6XL_icon.ico',
    bundle_identifier=None,
)
