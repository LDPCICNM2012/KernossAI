#!/usr/bin/env python3
"""
KernossAI — Compilador Multiplataforma de Escritorio
Empaqueta automaticamente KernossAI para el sistema
operativo actual (Windows, macOS o Linux) utilizando
PyInstaller con CustomTkinter, Matplotlib, E2EE,
recursos graficos y modulos completos.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# Asegurar codificacion UTF-8 segura en Windows y otros entornos
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Directorio raiz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGE_DIR = PROJECT_ROOT / "KernossAI"

def safe_print(msg: str):
    """Imprime mensajes de forma segura evitando errores de codificacion en Windows cp1252."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))

def print_banner(msg: str):
    safe_print("\n" + "=" * 60)
    safe_print(f" [*] {msg}")
    safe_print("=" * 60 + "\n")

def check_requirements():
    """Verifica e instala dependencias de compilacion si no estan presentes."""
    safe_print("[INFO] Verificando dependencias de compilacion...")
    try:
        import PyInstaller
        safe_print(f"[OK] PyInstaller detectado (v{PyInstaller.__version__})")
    except ImportError:
        safe_print("[BUILD] Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build():
    check_requirements()
    
    current_os = platform.system().lower()
    print_banner(f"Compilando KernossAI para {platform.system()} ({platform.machine()})")

    sep = ";" if current_os == "windows" else ":"

    # Datos adicionales a incluir
    datas = [
        f"{PACKAGE_DIR}{sep}KernossAI",
    ]

    # Iconos
    icon_ico = PACKAGE_DIR / "logo.ico"
    icon_icns = PACKAGE_DIR / "logo.icns"
    icon_png = PACKAGE_DIR / "logo.png"

    # Hidden imports requeridos
    hidden_imports = [
        "customtkinter",
        "PIL",
        "PIL.Image",
        "matplotlib",
        "matplotlib.pyplot",
        "matplotlib.backends.backend_tkagg",
        "numpy",
        "requests",
        "docx",
        "edge_tts",
        "cryptography",
        "google.genai",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "json",
        "uuid",
        "hashlib",
        "hmac",
        "secrets",
        "base64",
    ]

    main_script = str(PROJECT_ROOT / "main.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "KernossAI",
        "--clean",
        "--collect-all", "customtkinter",
        "--collect-all", "edge_tts",
    ]

    for data in datas:
        cmd.extend(["--add-data", data])

    for hi in hidden_imports:
        cmd.extend(["--hidden-import", hi])

    if current_os == "windows":
        if icon_ico.exists():
            cmd.extend(["--icon", str(icon_ico)])
    elif current_os == "darwin":
        if icon_icns.exists():
            cmd.extend(["--icon", str(icon_icns)])
        cmd.extend([
            "--osx-bundle-identifier", "com.kernossai.app"
        ])
    elif current_os == "linux":
        if icon_png.exists():
            cmd.extend(["--icon", str(icon_png)])
        elif icon_ico.exists():
            cmd.extend(["--icon", str(icon_ico)])

    cmd.append(main_script)

    safe_print("[BUILD] Ejecutando PyInstaller...")
    safe_print(f"[CMD] {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        safe_print("\n[ERROR] Error durante la compilacion con PyInstaller.")
        sys.exit(result.returncode)

    dist_dir = PROJECT_ROOT / "dist" / "KernossAI"
    print_banner("Compilacion completada con exito!")
    safe_print(f"[OUTPUT] Los archivos ejecutables se encuentran en:")
    safe_print(f"         {dist_dir}\n")

    if current_os == "windows":
        safe_print("[INFO] Para ejecutar KernossAI en Windows, abre:")
        safe_print(f"       {dist_dir / 'KernossAI.exe'}")
    elif current_os == "darwin":
        safe_print("[INFO] Para ejecutar KernossAI en macOS, abre:")
        safe_print(f"       {PROJECT_ROOT / 'dist' / 'KernossAI.app'}")
    else:
        safe_print("[INFO] Para ejecutar KernossAI en Linux, ejecuta:")
        safe_print(f"       {dist_dir / 'KernossAI'}")

if __name__ == "__main__":
    build()
