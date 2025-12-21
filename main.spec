# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs

a = Analysis(
    ['main.py'],
    pathex=[],
    datas=[(r'C:\Users\10648\AppData\Roaming\Python\Python39\site-packages\cuda\**', 'cuda')],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    binaries=collect_dynamic_libs('cuda') +[('utils/rzctl.dll', 'utils'),('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin/*.dll', '.')],  # 添加DLL
    hiddenimports=collect_submodules('cuda.bindings')+['site'] # ('cuda.bindings')['torch', 'cv2', 'pynput','cuda','cuda.bindings','cuda.bindings._bindings','cuda.bindings.cydriver','cuda.bindings.runtime','cuda.bindings.driver','cuda.bindings._lib','cuda.bindings._lib.utils','cuda.cudart']补充隐式导入
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
