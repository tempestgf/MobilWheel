# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ServerApp.py'],
    pathex=[],
    binaries=[],
    datas=[('azure.tcl', '.'), ('app_icon.ico', '.'), ('theme', 'theme'), ('vJoy', 'vJoy'), ('pylmusharedmemory', 'pylmusharedmemory')],
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
    name='ServerApp',
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
    icon=['app_icon.ico'],
)
