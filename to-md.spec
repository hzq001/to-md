# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hidden_imports = [
    'math',
    'multiprocessing',
    'multiprocessing.pool',
    'multiprocessing.managers',
    'multiprocessing.popen_spawn_posix',
    'multiprocessing.popen_fork',
    'multiprocessing.popen_spawn_win32',
    'multiprocessing.popen_forkserver',
    'multiprocessing.synchronize',
    'multiprocessing.heap',
    'multiprocessing.resource_tracker',
    'multiprocessing.spawn',
    'multiprocessing.util',
    'threading',
    'queue',
    'selectors',
    'logging',
    'typing'
]

a = Analysis(
    ['to_md/cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='to-md',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
