# -*- mode: python -*-
#
# pyinstaller f-engrave.py --clean -y --windowed --onefile
# pyinstaller -y --clean f-engrave.spec
# python -OO -m PyInstaller -y --clean f-engrave.spec
#
import os
HOMEBREW_PREFIX = os.environ['HOMEBREW_PREFIX']

POTRACE_BIN = HOMEBREW_PREFIX + '/bin/potrace'
POTRACE_LIB = HOMEBREW_PREFIX + '/lib/libpotrace*.dylib'

block_cipher = None

a = Analysis(['f-engrave.py'],
             pathex=['/Users/houser/Projects/f-engrave'],
             binaries=[('TTF2CXF_STREAM/ttf2cxf_stream', '.'), (POTRACE_BIN, '.'), (POTRACE_LIB, '.')],
             datas=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='f-engrave',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False
		)

app = BUNDLE(exe,
            name='F-Engrave.app',
            icon='fengrave.icns',
            bundle_identifier=None,
			info_plist={
				'NSPrincipleClass': 'NSApplication',
				'NSAppleScriptEnabled': False,
                'NSHighResolutionCapable': 'True',
				'CFBundleIdentifier': 'com.scorchworks.f-engrave',
				'CFBundleName': 'F-Engrave',
				'CFBundleDisplayName': 'F-Engrave',
				'CFBundleShortVersionString': '1.75'
				}
			)
