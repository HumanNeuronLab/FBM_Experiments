# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import pkg_resources
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [(pkg_resources.resource_filename('arabic_reshaper', 'default-config.ini'),
                'arabic_reshaper'),
                (pkg_resources.resource_filename('arabic_reshaper', '__version__.py'),
                'arabic_reshaper'),
                (pkg_resources.resource_filename('freetype', 'freetype.dll'),
                'freetype')]

datas += collect_data_files('psychopy')

psychopymodules = collect_submodules('psychopy')


a = Analysis(['CategoryLocalizer_Audio119.py'],
             binaries=[],
             datas=datas,
             hiddenimports=psychopymodules,
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='CL_Audio119_20240105',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
