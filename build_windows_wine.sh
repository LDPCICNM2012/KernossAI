#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# KernossAI — Compilador de Windows (.exe y Setup) desde Arch Linux usando Wine
# ─────────────────────────────────────────────────────────────────────────────

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "  KernossAI — Compilación de Windows (.exe) desde Arch Linux"
echo "============================================================"
echo ""

# 1. Comprobar si Wine está instalado
if ! command -v wine &> /dev/null; then
    echo "⚠️ Wine no está instalado en tu sistema Arch Linux."
    echo "Para compilar binarios de Windows (.exe) localmente en Arch, instala Wine:"
    echo ""
    echo "    sudo pacman -S wine winetricks"
    echo ""
    exit 1
fi

WINEPREFIX="${WINEPREFIX:-$HOME/.wine-kernossai-build}"
export WINEPREFIX
export WINEARCH=win64
export WINEDEBUG=-all

echo "🍷 Usando prefijo de Wine: $WINEPREFIX"
mkdir -p "$WINEPREFIX"

# 2. Descargar e instalar Python para Windows dentro de Wine si no existe
PYTHON_WIN="$WINEPREFIX/drive_c/Python311/python.exe"
if [ ! -f "$PYTHON_WIN" ]; then
    echo "📥 Descargando e instalando Python 3.11 para Windows en Wine..."
    TMP_DIR="/tmp/wine_python_setup"
    mkdir -p "$TMP_DIR"
    PYTHON_INSTALLER="$TMP_DIR/python-3.11.9-amd64.exe"
    
    if [ ! -f "$PYTHON_INSTALLER" ]; then
        curl -L -o "$PYTHON_INSTALLER" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    fi
    
    echo "Instalando Python en Wine (silencioso)..."
    wine "$PYTHON_INSTALLER" /quiet InstallAllUsers=1 PrependPath=1 TargetDir="C:\\Python311"
    
    # Esperar a que Wine termine la instalación
    wineserver -w
fi

echo "📦 Instalando dependencias de KernossAI en el entorno de Windows..."
wine "$PYTHON_WIN" -m pip install --upgrade pip
wine "$PYTHON_WIN" -m pip install -r requirements.txt
wine "$PYTHON_WIN" -m pip install pyinstaller

echo ""
echo "⚙️ Compilando KernossAI.exe para Windows..."
wine "$PYTHON_WIN" build_desktop.py

# 3. Comprobar Inno Setup en Wine
INNO_PATH="$WINEPREFIX/drive_c/Program Files (x86)/Inno Setup 6/ISCC.exe"
if [ ! -f "$INNO_PATH" ]; then
    INNO_PATH="$WINEPREFIX/drive_c/Program Files/Inno Setup 6/ISCC.exe"
fi

if [ -f "$INNO_PATH" ]; then
    echo ""
    echo "📦 Compilando Instalador Setup (.exe) con Inno Setup en Wine..."
    wine "$INNO_PATH" installer_windows.iss
    echo "✅ Setup generado en: dist/installer/KernossAI_Setup_v1.6.exe"
else
    echo ""
    echo "💡 Para generar también el instalador (.exe Setup) en Wine:"
    echo "   Descarga Inno Setup de https://jrsoftware.org/isdl.php y ejecútalo con:"
    echo "   wine innosetup-6.x.x.exe"
fi

echo ""
echo "============================================================"
echo "  🎉 ¡PROCESO DE WINDOWS FINALIZADO EN ARCH LINUX!"
echo "  Ejecutable portable: dist/KernossAI/KernossAI.exe"
echo "============================================================"
