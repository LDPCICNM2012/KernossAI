"""
KernossAI - Punto de Entrada Principal del Paquete
Ejecución del ciclo de vida, autenticación de sesión y arranque de la interfaz gráfica.
"""

import sys
from KernossAI.core.auth import token_guardado
from KernossAI.ui.login.login_window import PantallaLogin
from KernossAI.ui.modulos.dashboard import DashboardEstudios


def main():
    """Función principal de inicio de KernossAI."""
    # Desactivar __spec__ si es necesario para compatibilidad PyInstaller
    global __spec__
    __spec__ = None

    # 1. Intentar restaurar sesión persistida mediante token JWT
    _, sesion = token_guardado()

    # 2. Si no hay sesión válida o ha caducado, solicitar inicio de sesión
    if not sesion:
        pantalla_login = PantallaLogin()
        pantalla_login.mainloop()
        sesion = pantalla_login.usuario_autenticado

    # 3. Si el usuario se autenticó exitosamente, iniciar Dashboard
    if sesion:
        app = DashboardEstudios(sesion)
        app.protocol("WM_DELETE_WINDOW", app._al_cerrar)
        app.mainloop()


if __name__ == "__main__":
    main()
