#!/usr/bin/env python3
"""
KernossAI — Compilador Multiplataforma de Escritorio
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Empaqueta automáticamente KernossAI para el sistema
operativo actual (Windows, macOS o Linux) utilizando
PyInstaller con CustomTkinter, Matplotlib, E2EE,
recursos gráficos y módulos completos.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# Directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent
PACKAGE_DIR = PROJECT_ROOT / "KernossAI"

def print_banner(msg: str):
    print("\n" + "═" * 60)
    print(f" 🚀 {msg}")
    print("═" * 60 + "\n")

def check_requirements():
    """Verifica e instala dependencias de compilación si no están presentes."""
    print("📦 Verificando dependencias de compilación...")
    try:
        import PyInstaller
        print(f"✓ PyInstaller detectado (v{PyInstaller.__version__})")
    except ImportError:
        print("Instalando PyInstaller...")
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

    print("Ejecutando PyInstaller...")
    print(f"Comando: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print("\n❌ Error durante la compilación.")
        sys.exit(result.returncode)

    dist_dir = PROJECT_ROOT / "dist" / "KernossAI"
    print_banner("¡Compilación completada con éxito!")
    print(f"📁 Los archivos ejecutables se encuentran en:")
    print(f"   {dist_dir}\n")

    if current_os == "windows":
        print("💡 Para ejecutar KernossAI en Windows, abre:")
        print(f"   {dist_dir / 'KernossAI.exe'}")
    elif current_os == "darwin":
        print("💡 Para ejecutar KernossAI en macOS, abre:")
        print(f"   {PROJECT_ROOT / 'dist' / 'KernossAI.app'}")
    else:
        print("💡 Para ejecutar KernossAI en Linux, ejecuta:")
        print(f"   {dist_dir / 'KernossAI'}")

if __name__ == "__main__":
    build()
