"""
KernossAI UI Modals - Ventanas modulares de configuración, soporte, moderación, tutoría y novedades.
"""

from KernossAI.ui.modals.soporte import VentanaSoporteE2EE, VentanaBandejaSoporte
from KernossAI.ui.modals.moderacion import VentanaAdminModeracion
from KernossAI.ui.modals.ajustes import VentanaAjustes, ModalAgregarCuenta
from KernossAI.ui.modals.novedades import VentanaNovedadesIA
from KernossAI.ui.modals.tutoria import VentanaTutoriaAlumnoProfesor
from KernossAI.ui.modals.privacidad import (
    VentanaPoliticaPrivacidad,
    esta_politica_aceptada,
    registrar_aceptacion_politica,
)
