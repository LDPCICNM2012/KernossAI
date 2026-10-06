#!/bin/bash
# ─────────────────────────────────────────────────────────────
# KernossAI — Compilador para macOS (.app y .dmg Instalador)
# ─────────────────────────────────────────────────────────────

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT="$DIR/.."
cd "$PROJECT_ROOT"

echo "============================================================"
echo "  KernossAI — Compilación Nativa para macOS (.app y .dmg)"
echo "============================================================"
echo ""

# Usar Python del entorno virtual o python3
if [ -f "$DIR/../../myvenv/bin/python" ]; then
    PYTHON_EXEC="$DIR/../../myvenv/bin/python"
elif [ -f "$DIR/../myvenv/bin/python" ]; then
    PYTHON_EXEC="$DIR/../myvenv/bin/python"
else
    PYTHON_EXEC="python3"
fi

echo "📦 [1/3] Verificando dependencias de Python..."
$PYTHON_EXEC -m pip install --upgrade pip
$PYTHON_EXEC -m pip install -r requirements.txt
$PYTHON_EXEC -m pip install pyinstaller

echo ""
echo "⚙️ [2/3] Compilando aplicación empaquetada (.app) con PyInstaller..."
$PYTHON_EXEC scripts/build_desktop.py

echo ""
echo "💿 [3/3] Generando instalador de imagen de disco (.dmg)..."

DMG_TEMP="$PROJECT_ROOT/dist/dmg_staging"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# Copiar el .app al directorio temporal de empaquetado DMG
if [ -d "$PROJECT_ROOT/dist/KernossAI.app" ]; then
    cp -R "$PROJECT_ROOT/dist/KernossAI.app" "$DMG_TEMP/"
elif [ -d "$PROJECT_ROOT/dist/KernossAI/KernossAI.app" ]; then
    cp -R "$PROJECT_ROOT/dist/KernossAI/KernossAI.app" "$DMG_TEMP/"
else
    echo "⚠️ No se encontró dist/KernossAI.app, buscando estructura generada..."
    mkdir -p "$DMG_TEMP/KernossAI"
    cp -R "$PROJECT_ROOT/dist/KernossAI/"* "$DMG_TEMP/KernossAI/"
fi

# Crear acceso directo arrastrable a /Applications
ln -s /Applications "$DMG_TEMP/Applications"

# Crear la imagen .dmg usando la herramienta nativa de macOS hdiutil
mkdir -p "$PROJECT_ROOT/dist"
ARCH_NAME="${MAC_ARCH:-$(uname -m)}"
DMG_NAME="${DMG_OUTPUT_NAME:-KernossAI_macOS_${ARCH_NAME}.dmg}"
DMG_OUTPUT="$PROJECT_ROOT/dist/$DMG_NAME"
rm -f "$DMG_OUTPUT"

hdiutil create -volname "KernossAI Installer" -srcfolder "$DMG_TEMP" -ov -format UDZO "$DMG_OUTPUT"

# Copia de compatibilidad genérica
cp -f "$DMG_OUTPUT" "$PROJECT_ROOT/dist/KernossAI_macOS_Installer.dmg"

# Limpieza
rm -rf "$DMG_TEMP"

echo ""
echo "============================================================"
echo "  🎉 ¡COMPILACIÓN EXITOSA EN MACOS ($ARCH_NAME)!"
echo "  Aplicación ejecutable: dist/KernossAI.app"
echo "  Instalador de disco:   dist/$DMG_NAME"
echo "============================================================"
