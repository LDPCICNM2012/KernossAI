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

    # 1. Comprobación obligatoria de Política de Privacidad & RGPD al iniciar la app
    import os
    import customtkinter as ctk
    from KernossAI.ui.modals.privacidad import esta_politica_aceptada, VentanaPoliticaPrivacidad

    if not esta_politica_aceptada():
        ventana_init = ctk.CTk()
        ventana_init.withdraw()

        estado = [False]

        def _al_aceptar():
            estado[0] = True
            ventana_init.destroy()

        def _al_rechazar():
            ventana_init.destroy()
            os._exit(0)

        modal = VentanaPoliticaPrivacidad(
            ventana_init,
            modo_inicio=True,
            on_aceptar=_al_aceptar,
            on_rechazar=_al_rechazar
        )
        modal.protocol("WM_DELETE_WINDOW", _al_rechazar)
        ventana_init.mainloop()

        if not estado[0]:
            os._exit(0)

    # 2. Intentar restaurar sesión persistida mediante token JWT
    _, sesion = token_guardado()

    # 3. Si no hay sesión válida o ha caducado, solicitar inicio de sesión
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
