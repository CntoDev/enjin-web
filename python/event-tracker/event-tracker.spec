# -*- mode: python -*-
a = Analysis(['event-tracker.py'],
             pathex=['C:\\Python27\\Lib\\site-packages', 'C:\\Dev\\cnto-web\\python\\event-tracker'],
             hiddenimports=['lxml._elementpath', 'gzip'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='event-tracker.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
