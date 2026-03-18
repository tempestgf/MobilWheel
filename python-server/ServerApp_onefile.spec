# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['ServerApp.py'],
    pathex=[],
    binaries=[],
    datas=[('azure.tcl', '.'), ('app_logo.ico', '.'), ('theme', 'theme'), ('vJoy', 'vJoy'), ('pylmusharedmemory', 'pylmusharedmemory')],
    hiddenimports=['xbox', 'game_telemetry', 'updater', 'app_version'],
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
    name='MobileWheelServer-1.0.1-setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app_logo.ico'],
)
