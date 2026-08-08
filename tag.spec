# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tag.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'taglib',
    ],
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
    name='MusicTagEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # 不显示终端窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # 可指定 .icns 图标路径
)

app = BUNDLE(
    exe,
    name='MusicTagEditor.app',
    bundle_identifier='com.example.musictageditor',
    icon=None,              # 可指定 .icns
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleDisplayName': '音乐标签编辑器',
        'CFBundleName': 'MusicTagEditor',
        'CFBundleShortVersionString': '3.0.0',
        'CFBundleVersion': '3.0.0',
        'LSMinimumSystemVersion': '10.13',
    },
)