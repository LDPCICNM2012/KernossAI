# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Recoger dinámicamente recursos de librerías complejas
mpl_datas, mpl_binaries, mpl_hiddenimports = collect_all('matplotlib')
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

block_cipher = None

# ───── ANÁLISIS DEL MAIN Y SUS DEPENDENCIAS ─────
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[] + mpl_binaries + ctk_binaries,
    datas=[
        ('Calculador_Notas_Tkinter_FINAL.py', '.'),
        ('Apuntador_Notas_Visual.py', '.'),
        ('resumidor_de_textos_visual.py', '.'),
        ('generador_examen_visual.py', '.'),
        ('Ayudador_de_problemas_visual.py', '.'),
        ('Calendario_FINAL.py', '.'),  # <--- Módulo de la Agenda añadido correctamente
        ('logo.icns', '.'),
    ] + mpl_datas + ctk_datas,
    hiddenimports=[
        'PIL',
        'PIL._imagingtk',
        'PIL.ImageTk',
        # Forzar backends de gráficos explícitamente en macOS
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends._backend_tk',
        'matplotlib.backends.backend_macosx',
        'docx',
        'docx.shared',
        'docx.enum.text',
        'ollama',
        'numpy',
        'threading',
        'json',
    ] + mpl_hiddenimports + ctk_hiddenimports,
    hookspath=[],
    hooksconfig={
        # Forzar a PyInstaller a incluir TkAgg en lugar de solo MacOSX nativo para evitar crasheos de GUI
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
    [],
    exclude_binaries=True,
    name='Immune Study Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Falso oculta la ventana negra de comandos (Terminal) en producción
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.icns'],
)

# ───── RECOPILACIÓN DEL CONTENIDO INTERNO ─────
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Immune Study Suite',
)

# ───── EMPAQUETADO FINAL EN BUNDLE MAC (.APP) ─────
app = BUNDLE(
    coll,
    name='Immune Study Suite.app',
    icon='logo.icns',
    bundle_identifier='com.immune.studysuite',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
    },
)