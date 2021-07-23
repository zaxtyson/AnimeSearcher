# -*- mode: python ; coding: utf-8 -*-

# 本文件用于打包 Windows 程序
# 建议在虚拟环境下打包
# pyinstaller --clean -F build_exe.spec

block_cipher = None

# 繁简体转换库 zhconv 中的 json 路径
zhconv_data_path = 'zhconv/zhcdict.json'

AnalysisList = [
    'ui.pyw',
    'api/danmaku/bilibili/__init__.py',  # 否则找不到模块 google.protobuf
    'api/anime/bimibimi.py'  # 用于分析 Crypto 的依赖
    ]

a = Analysis(AnalysisList,
             pathex=['.'],
             datas=[
                ('web','web'),
                ('api', 'api'),
                ('logo.ico', '.'),
                (zhconv_data_path, 'zhconv')
                ],
             binaries=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='AnimeSearcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='AnimeSearcher')
