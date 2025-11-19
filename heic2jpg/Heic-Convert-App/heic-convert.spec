# -*- mode: python ; coding: utf-8 -*-

import shutil

a = Analysis(
    ['heic-convert.py'],
    pathex=[],
    binaries=[],
    datas=[('translations.json', '.'), ('images-regular-full.ico', '.'), ('images-regular-full.png', '.')],
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
    name='heic-convert',
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
    icon=['images-regular-full.ico'],
)

shutil.copy("install.sh", DISTPATH)
shutil.copy("images-regular-full.svg", DISTPATH)
