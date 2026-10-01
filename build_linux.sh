#!/bin/bash
# ─────────────────────────────────────────────────────────────
# KernossAI — Compilador para Linux (Arch Linux, Ubuntu, Debian, Fedora)
# ─────────────────────────────────────────────────────────────

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "  KernossAI — Compilación Nativa para Linux / Arch Linux"
echo "============================================================"
echo ""

# Usar el entorno virtual si existe
if [ -f "$DIR/../myvenv/bin/python" ]; then
    PYTHON_EXEC="$DIR/../myvenv/bin/python"
else
    PYTHON_EXEC="python3"
fi

echo "📦 [1/4] Verificando dependencias..."
$PYTHON_EXEC -m pip install --upgrade pip
$PYTHON_EXEC -m pip install -r requirements.txt
$PYTHON_EXEC -m pip install pyinstaller

echo ""
echo "⚙️ [2/4] Compilando binario de Linux con PyInstaller..."
$PYTHON_EXEC build_desktop.py

echo ""
echo "📝 [3/4] Generando lanzador de escritorio (.desktop) e icono..."
cat << 'EOF' > dist/KernossAI/kernossai.desktop
[Desktop Entry]
Name=KernossAI
Comment=Plataforma Integral de Inteligencia Artificial para el Estudio y la Enseñanza
Exec=./KernossAI
Icon=logo
Terminal=false
Type=Application
Categories=Education;Science;Office;Utility;
StartupWMClass=KernossAI
EOF

if [ -f "KernossAI/logo.png" ]; then
    cp KernossAI/logo.png dist/KernossAI/logo.png
fi

chmod +x dist/KernossAI/KernossAI
chmod +x dist/KernossAI/kernossai.desktop

echo ""
echo "📦 [4/4] Creando paquete comprimido para distribución (.tar.gz)..."
cd dist
tar -czf KernossAI_Linux_x86_64.tar.gz KernossAI
cd ..

echo ""
echo "============================================================"
echo "  🎉 ¡COMPILACIÓN EXITOSA EN LINUX / ARCH LINUX!"
echo "  Binario ejecutable: dist/KernossAI/KernossAI"
echo "  Lanzador desktop:   dist/KernossAI/kernossai.desktop"
echo "  Paquete Tarball:    dist/KernossAI_Linux_x86_64.tar.gz"
echo "============================================================"
