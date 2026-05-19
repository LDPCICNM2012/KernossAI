# ─────────────────────────────────────────────────────────────────────────────
#  Immune Study Suite 2026 — PyInstaller SPEC (Windows)
#  Genera: dist/Immune Study Suite.exe  (todo-en-uno, sin carpetas)
#
#  INSTRUCCIONES RÁPIDAS:
#    1. Coloca este .spec en la misma carpeta que todos los .py y el logo.ico
#    2. Abre CMD / PowerShell en esa carpeta
#    3. Ejecuta:  pyinstaller build_windows.spec
#    4. El .exe estará en dist/  — puedes borrar build/ y dist/ excepto el .exe
# ─────────────────────────────────────────────────────────────────────────────

import os

# Raíz del proyecto (donde está este .spec)
ROOT = os.path.dirname(os.path.abspath(SPEC))

# ── Todos los scripts secundarios que el dashboard lanzará en subprocess ──
scripts_secundarios = [
    "Calculador_Notas_Tkinter_FINAL.py",
    "Apuntador_Notas_Visual.py",
    "resumidor_de_textos_visual.py",
    "generador_examen_visual.py",
    "Ayudador_de_problemas_visual.py",
    "Calendario_FINAL.py",
]

# ── Datos extra a empaquetar dentro del EXE (scripts + icono) ──
datas_list = [
    (os.path.join(ROOT, "logo.ico"), "."),
]
for s in scripts_secundarios:
    datas_list.append((os.path.join(ROOT, s), "."))

# ── Imports ocultos necesarios para que CustomTkinter y matplotlib no fallen ──
hidden = [
    "customtkinter",
    "PIL._tkinter_finder",
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "matplotlib.backends._backend_tk",
    "numpy",
    "openai",
    "docx",
    "json",
    "threading",
    "calendar",
    "subprocess",
]

# ─────────────── BLOQUE ANALYSIS ───────────────
a = Analysis(
    [os.path.join(ROOT, "main.py")],   # Punto de entrada principal (Windows)
    pathex=[ROOT],
    binaries=[],
    datas=datas_list,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    noarchive=False,
)

# ─────────────── BLOQUE PYZ (bytecode comprimido) ───────────────
pyz = PYZ(a.pure)

# ─────────────── BLOQUE EXE (ejecutable único) ───────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Immune Study Suite",          # Nombre final del .exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                           # Compresión UPX (si está instalado)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                      # Sin ventana de consola negra
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "logo.ico"),  # Icono del ejecutable
    onefile=True,                       # TODO EN UN SOLO .exe
)

# ─────────────────────────────────────────────────────────────────────────────
#  NOTA POST-BUILD:
#  Tras ejecutar pyinstaller, puedes borrar la carpeta "build/" sin problema.
#  El EXE final es únicamente:  dist/Immune Study Suite.exe
#  No necesita ninguna DLL, carpeta ni archivo adicional para funcionar.
# ─────────────────────────────────────────────────────────────────────────────
