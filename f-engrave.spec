# -*- mode: python ; coding: utf-8 -*-

# pyinstaller --clean -y --windowed --onedir f-engrave.py 
# pyinstaller -y --clean f-engrave.spec
# python -OO -m PyInstaller -y --clean f-engrave.spec

block_cipher = None

a = Analysis(['f-engrave.py'],
             pathex=['/Users/houser/Projects/f-engrave'],
             binaries=[('TTF2CXF_STREAM/ttf2cxf_stream', '.'),
                        ('/usr/local/bin/potrace', '.'),
                        ('/usr/local/lib/libpotrace.0.dylib', '.'),
                        ('/usr/local/lib/libfreetype.6.dylib', '.'),
                        ('/usr/local/lib/libpng16.16.dylib', '.')],             
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
          [],
          exclude_binaries=True,
          name='f-engrave',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='f-engrave')

app = BUNDLE(coll,
            name='F-Engrave.app',
            icon='fengrave.icns',
            bundle_identifier=None,
			info_plist={
				'NSPrincipleClass': 'NSApplication',
                'NSHighResolutionCapable': 'True',
				'NSAppleScriptEnabled': False,
				'CFBundleIdentifier': 'com.scorchworks.f-engrave',
				'CFBundleName': 'F-Engrave',
				'CFBundleDisplayName': 'F-Engrave',
				'CFBundleShortVersionString': '1.68'
				}
            )
