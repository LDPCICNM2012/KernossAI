# ─────────────────────────────────────────────────────────────────────────────
#  Immune Study Suite 2026 — PyInstaller SPEC (macOS)
#  Genera: dist/Immune Study Suite.app  (bundle todo-en-uno, sin carpetas)
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
import customtkinter

ROOT = os.path.dirname(os.path.abspath(SPEC))

scripts_secundarios = [
    "Calculador_Notas_Tkinter_FINAL.py",
    "Apuntador_Notas_Visual.py",
    "resumidor_de_textos_visual.py",
    "generador_examen_visual.py",
    "Ayudador_de_problemas_visual.py",
    "Calendario_FINAL.py",
]

# Conseguimos la ruta exacta de customtkinter para inyectar sus temas json
ctk_dir = os.path.dirname(customtkinter.__file__)

datas_list = [
    (os.path.join(ROOT, "logo.icns"), "."),
    (ctk_dir, "customtkinter"),
]
for s in scripts_secundarios:
    datas_list.append((os.path.join(ROOT, s), "."))

hidden = [
    "customtkinter",
    "PIL._tkinter_finder",
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "numpy",
    "docx",
    "openai",
    "httpx",
]

a = Analysis(
    ['main_macos_.py'],
    pathex=[ROOT],
    binaries=[],
    datas=datas_list,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[], # ¡CORRECCIÓN CRÍTICA! Vaciado para permitir unittest, tkinter.test, etc.
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
    upx=False,  
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "logo.icns"),
)

# ─────────────── BLOQUE BUNDLE (.app) ───────────────
app = BUNDLE(
    exe,
    name="Immune Study Suite.app",
    icon=os.path.join(ROOT, "logo.icns"),
    bundle_identifier="com.immune.studysuite",
    info_plist={
        "CFBundleName": "Immune Study Suite",
        "CFBundleDisplayName": "Immune Study Suite",
        "CFBundleVersion": "2.0.0",
        "CFBundleShortVersionString": "2.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSMinimumSystemVersion": "10.15",
        "CFBundleDocumentTypes": [],
    },
)