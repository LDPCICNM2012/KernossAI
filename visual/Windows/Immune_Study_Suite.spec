# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Recoger dinámicamente recursos de librerías complejas
mpl_datas, mpl_binaries, mpl_hiddenimports = collect_all('matplotlib')
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')
openai_datas, openai_binaries, openai_hiddenimports = collect_all('openai')
httpx_datas, httpx_binaries, httpx_hiddenimports = collect_all('httpx')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[] + mpl_binaries + ctk_binaries + openai_binaries + httpx_binaries,
    datas=[
        ('Calculador_Notas_Tkinter_FINAL.py', '.'),
        ('Apuntador_Notas_Visual.py', '.'),
        ('resumidor_de_textos_visual.py', '.'),
        ('generador_examen_visual.py', '.'),
        ('Ayudador_de_problemas_visual.py', '.'),
        ('Calendario_FINAL.py', '.'),
    ] + mpl_datas + ctk_datas + openai_datas + httpx_datas,
    hiddenimports=[
        'PIL',
        'PIL._imagingtk',
        'PIL.ImageTk',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends._backend_tk',
        'docx',
        'docx.shared',
        'docx.enum.text',
        'numpy',
        'threading',
        'json',
        'anyio',
        'httpcore',
        'pydantic',
    ] + mpl_hiddenimports + ctk_hiddenimports + openai_hiddenimports + httpx_hiddenimports,
    hookspath=[],
    hooksconfig={
        'matplotlib': {
            'backends': 'TkAgg',
        },
    },
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,     # Empaqueta los binarios dentro del EXE único
    a.zipfiles,     # Empaqueta las librerías comprimidas dentro del EXE único
    a.datas,        # Empaqueta los scripts secundarios (.py) dentro del EXE único
    name='Immune Study Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # Oculta la terminal negra de Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)