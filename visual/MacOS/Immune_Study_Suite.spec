# ─────────────────────────────────────────────────────────────────────────────
#  Immune Study Suite 2026 — PyInstaller SPEC (macOS)
#  Genera: dist/Immune Study Suite.app  (bundle todo-en-uno, sin carpetas)
#
#  INSTRUCCIONES RÁPIDAS:
#    1. Coloca este .spec en la misma carpeta que todos los .py y el logo.ico
#    2. Abre Terminal en esa carpeta
#    3. Ejecuta:  pyinstaller build_macos.spec
#    4. El .app estará en dist/  — puedes borrar build/ y dist/ excepto el .app
#
#  REQUISITO: pip install pyinstaller customtkinter openai python-docx
#             matplotlib numpy pillow
# ─────────────────────────────────────────────────────────────────────────────

import os

ROOT = os.path.dirname(os.path.abspath(SPEC))

scripts_secundarios = [
    "Calculador_Notas_Tkinter_FINAL.py",
    "Apuntador_Notas_Visual.py",
    "resumidor_de_textos_visual.py",
    "generador_examen_visual.py",
    "Ayudador_de_problemas_visual.py",
    "Calendario_FINAL.py",
]

datas_list = [
    (os.path.join(ROOT, "logo.ico"), "."),
]
for s in scripts_secundarios:
    datas_list.append((os.path.join(ROOT, s), "."))

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
    [os.path.join(ROOT, "main_macos_.py")],   # Punto de entrada (macOS)
    pathex=[ROOT],
    binaries=[],
    datas=datas_list,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "email",
        "xml",
        "pydoc",
        "doctest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Immune Study Suite",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX no es recomendable en macOS (puede romper la firma)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,   # El enrutador manual del main ya lo gestiona
    target_arch=None,       # Cambiar a "x86_64" o "arm64" si necesitas forzar arquitectura
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "logo.ico"),
)

# ─────────────── BLOQUE BUNDLE (.app) ───────────────
app = BUNDLE(
    exe,
    name="Immune Study Suite.app",
    icon=os.path.join(ROOT, "logo.ico"),
    bundle_identifier="com.immune.studysuite",
    info_plist={
        "CFBundleName": "Immune Study Suite",
        "CFBundleDisplayName": "Immune Study Suite",
        "CFBundleVersion": "2.0.0",
        "CFBundleShortVersionString": "2.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,  # Soporta Dark Mode nativo
        "LSMinimumSystemVersion": "10.15",
        "CFBundleDocumentTypes": [],
    },
)

# ─────────────────────────────────────────────────────────────────────────────
#  NOTA POST-BUILD:
#  Tras ejecutar pyinstaller, puedes borrar la carpeta "build/" sin problema.
#  El bundle final es únicamente: dist/Immune Study Suite.app
#  Para distribuir: comprime el .app en un .zip o crea un .dmg.
#  Si macOS avisa "no verificado": click derecho → Abrir la primera vez.
# ─────────────────────────────────────────────────────────────────────────────
