# Maintainer: Lander <lander@kernossai.com>
pkgname=kernossai-bin
pkgver=1.6.0
pkgrel=1
pkgdesc="Plataforma de Inteligencia Artificial para el Estudio y la Enseñanza"
arch=('x86_64')
url="https://github.com/lander/KernossAI"
license=('Proprietary')
depends=('gtk3' 'libnotify' 'alsa-lib')
options=('!strip')

package() {
    install -d "${pkgdir}/opt/kernossai"
    install -d "${pkgdir}/usr/bin"
    install -d "${pkgdir}/usr/share/applications"
    install -d "${pkgdir}/usr/share/pixmaps"

    # Copiar archivos compilados
    cp -r "${srcdir}/KernossAI/"* "${pkgdir}/opt/kernossai/"
    chmod 755 "${pkgdir}/opt/kernossai/KernossAI"

    # Enlace simbólico en /usr/bin
    ln -s /opt/kernossai/KernossAI "${pkgdir}/usr/bin/kernossai"

    # Instalar Icono y Desktop
    if [ -f "${srcdir}/KernossAI/logo.png" ]; then
        install -Dm644 "${srcdir}/KernossAI/logo.png" "${pkgdir}/usr/share/pixmaps/kernossai.png"
    fi

    cat << 'EOF' > "${pkgdir}/usr/share/applications/kernossai.desktop"
[Desktop Entry]
Name=KernossAI
Comment=Plataforma de IA para el Estudio y la Enseñanza
Exec=/usr/bin/kernossai
Icon=kernossai
Terminal=false
Type=Application
Categories=Education;Science;Office;
StartupWMClass=KernossAI
EOF
    chmod 644 "${pkgdir}/usr/share/applications/kernossai.desktop"
}
