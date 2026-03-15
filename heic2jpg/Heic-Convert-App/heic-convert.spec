# -*- mode: python ; coding: utf-8 -*-
import os
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

BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

install_script = os.path.join(BASE_DIR, "install.sh")
icon = os.path.join(BASE_DIR, "images-regular-full.svg")

shutil.copy(install_script, DISTPATH)
shutil.copy(icon, DISTPATH)
