# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Recoger dinámicamente recursos de librerías complejas de interfaz y gráficos
mpl_datas, mpl_binaries, mpl_hiddenimports = collect_all('matplotlib')
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

# 👇 RECOLECCIÓN CRUCIAL: Forzamos la integración completa de OpenAI y HTTPX 👇
openai_datas, openai_binaries, openai_hiddenimports = collect_all('openai')
httpx_datas, httpx_binaries, httpx_hiddenimports = collect_all('httpx')

block_cipher = None

# ───── ANÁLISIS DEL MAIN Y SUS DEPENDENCIAS ─────
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
        ('logo.icns', '.'),
    ] + mpl_datas + ctk_datas + openai_datas + httpx_datas,
    hiddenimports=[
        'PIL',
        'PIL._imagingtk',
        'PIL.ImageTk',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends._backend_tk',
        'matplotlib.backends.backend_macosx',
        'docx',
        'docx.shared',
        'docx.enum.text',
        'numpy',
        'threading',
        'json',
        'anyio',       # Requerido por el cliente HTTP asíncrono
        'httpcore',    # Motor de red subyacente de la IA
        'pydantic',    # Validador de datos que usa internamente OpenAI
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

# ───── CONFIGURACIÓN DEL EJECUTABLE BINARIO ─────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       
    a.zipfiles,       
    a.datas,          
    [],
    exclude_binaries=False,  
    name='Immune Study Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, 
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.icns'],
)

# ───── EMPAQUETADO FINAL EN BUNDLE MAC (.APP) ─────
app = BUNDLE(
    exe,              
    name='Immune Study Suite.app',
    icon='logo.icns',
    bundle_identifier='com.immune.studysuite',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
    },
)