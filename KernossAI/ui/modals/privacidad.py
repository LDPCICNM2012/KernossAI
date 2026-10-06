"""
KernossAI - Módulo de Privacidad, Aviso Legal y Protección de Datos (RGPD)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Marco normativo de protección de datos personales, derechos de los usuarios
y cláusulas de seguridad, auditoría e infraestructura técnica (IP/HWID).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

from KernossAI.core.theme import (
    COLOR_BG_DARK,
    COLOR_BG_CARD,
    COLOR_BG_CARD_LIGHT,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_SKY,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    aplicar_icono,
    centrar_ventana,
    VERSION_APP,
)

RUTA_ACEPTACION_POLITICA = os.path.expanduser("~/.kernoss_politica_privacidad_aceptada.json")


def esta_politica_aceptada() -> bool:
    """Comprueba si el usuario ya ha aceptado formalmente la política de privacidad."""
    if os.path.exists(RUTA_ACEPTACION_POLITICA):
        try:
            with open(RUTA_ACEPTACION_POLITICA, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("aceptado", False))
        except Exception:
            return False
    return False


def registrar_aceptacion_politica():
    """Guarda localmente la constancia de consentimiento explícito."""
    try:
        with open(RUTA_ACEPTACION_POLITICA, "w", encoding="utf-8") as f:
            json.dump({
                "aceptado": True,
                "version_politica": VERSION_APP,
                "fecha_consentimiento": datetime.now().isoformat(),
            }, f, indent=2)
    except Exception:
        pass


TEXTO_POLITICA_COMPLETO = f"""POLÍTICA DE PRIVACIDAD, AVISO LEGAL Y CONDICIONES DE SEGURIDAD
KernossAI Educational Suite — Versión Oficial v{VERSION_APP} (Conforme al RGPD UE 2016/679)
──────────────────────────────────────────────────────────────────────────────

1. IDENTIDAD DEL RESPONSABLE DEL TRATAMIENTO
KernossAI es una plataforma educativa de estudio, enseñanza y preparación académica.
Canal oficial de privacidad y protección de datos: kernossai@support.com.

2. TRATAMIENTO DE DIRECCIONES IP Y DISPOSITIVOS (MARCO LEGAL RGPD)
No, no es ilegal que el propietario de una aplicación vea la dirección IP de sus usuarios, ya que técnicamente es un dato necesario para que los servidores puedan enviar y recibir información de la app. Sin embargo, está sujeto a normas estrictas de privacidad y protección de datos (como el RGPD en Europa).

Aspectos clave a tener en cuenta:
• La IP es un dato personal: La Unión Europea considera la dirección IP como un dato de carácter personal porque, de manera directa o combinada con otros datos, puede llegar a identificar a una persona.
• Necesitas una base legal: Para recopilar, almacenar o tratar las IPs de tus usuarios, debes cumplir con el Reglamento General de Protección de Datos (RGPD). Esto significa que debes:
  - Informar al usuario en tu Política de Privacidad de que recoges esta información y con qué fin (por ejemplo, seguridad, registro de errores o funcionamiento técnico).
  - Tener una base jurídica válida (como el consentimiento del usuario o un interés legítimo para la seguridad del servicio).
• Seguridad y uso legítimo: Ver la IP de forma automática para que la aplicación funcione o para proteger el sistema ante ataques no es delito. Lo ilegal sería utilizarla para fines no declarados, cederla a terceros sin autorización o realizar actividades de espionaje o acoso.

3. FINALIDADES ESPECÍFICAS DEL TRATAMIENTO EN KERNOSSAI
Los datos técnicos (dirección IP, identificador de dispositivo HWID y registros de actividad) se procesan exclusivamente para:
a) Prestación del Servicio: Enrutamiento seguro de peticiones a los motores de Inteligencia Artificial (Groq y Google Gemini).
b) Detección y Prevención de Ciberataques: Mitigación de ataques de denegación de servicio (DDoS), inyecciones maliciosas y abuso automatizado de la API.
c) Política de Hogar de Estudio (Anti-Abuso): Prevenir la reventa, multicuentas fraudulentas y el uso indebido del servicio fuera del núcleo doméstico autorizado.
d) Sistema Disciplinario y Moderación: Aplicación de sanciones de Hardware-Ban o IP-Ban a usuarios que vulneren gravemente las normas de convivencia o intenten vulnerar la plataforma.

4. CONFIDENCIALIDAD Y CIFRADO DE DATOS (E2EE)
• Los apuntes, mapas conceptuales, ejercicios y borradores se procesan de forma segura.
• Las consultas dirigidas a soporte técnico a través del canal oficial cuentan con cifrado asimétrico de extremo a extremo (E2EE), asegurando que únicamente el personal autorizado de soporte (kernossai@support.com) pueda descifrar tus dudas técnicas.
• Queda terminantemente prohibida la comercialización, venta o cesión de datos personales o técnicos a terceros con fines publicitarios.

5. DERECHOS DEL USUARIO (DERECHOS ARCO-POL)
De conformidad con los artículos 15 a 22 del RGPD, todo usuario registrado tiene derecho a:
• Derecho de Acceso: Conocer qué datos personales y técnicos están asociados a su perfil.
• Derecho de Rectificación: Modificar información inexacta desde su panel de perfil o mediante solicitud.
• Derecho de Supresión (Derecho al Olvido): Solicitar la eliminación total e irreversible de su cuenta y registros desde Ajustes > Eliminar Cuenta.
• Derecho a la Limitación del Tratamiento y Oposición: Revocar el consentimiento en cualquier momento.
Para ejercer estos derechos de forma formal, puedes escribir a: kernossai@support.com.

6. OBLIGATORIEDAD DEL CONSENTIMIENTO
El consentimiento para el tratamiento legítimo de datos con fines de seguridad técnica es requisito indispensable para la utilización de la infraestructura de KernossAI. Si no aceptas estos términos, no podrás crear una cuenta ni utilizar la plataforma, debiendo cerrar la aplicación de inmediato.
"""


class _BasePoliticaUI:
    """Constructor visual compartido para la ventana de privacidad."""

    def _construir_contenido_politica(self, modo_inicio: bool = False, on_aceptar=None, on_rechazar=None):
        self.modo_inicio = modo_inicio
        self.on_aceptar = on_aceptar
        self.on_rechazar = on_rechazar

        # Contenedor raíz
        self.configure(fg_color=COLOR_BG_DARK)

        # 1. Cabecera visual
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, height=72, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        f_h_txt = ctk.CTkFrame(header, fg_color="transparent")
        f_h_txt.pack(side="left", padx=20, pady=12, fill="both", expand=True)

        f_tit_row = ctk.CTkFrame(f_h_txt, fg_color="transparent")
        f_tit_row.pack(anchor="w")

        ctk.CTkLabel(
            f_tit_row,
            text="📜 Política de Privacidad & Cumplimiento RGPD",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=COLOR_ACCENT_SKY
        ).pack(side="left")

        ctk.CTkLabel(
            f_tit_row,
            text=f" v{VERSION_APP} ",
            font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"),
            text_color="#38bdf8",
            fg_color="#0c2340",
            corner_radius=6
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            f_h_txt,
            text="Transparencia, tratamiento legal de datos de red (IP), confidencialidad y derechos de usuario.",
            font=ctk.CTkFont(family="Helvetica", size=11),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        if not self.modo_inicio:
            btn_cerrar_top = ctk.CTkButton(
                header, text="✕", width=36, height=36, fg_color=COLOR_BG_CARD,
                hover_color=COLOR_DANGER, font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
                command=self.destroy
            )
            btn_cerrar_top.pack(side="right", padx=18, pady=18)

        # 2. Caja de texto con la política de privacidad y formato
        self.txt_politica = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Helvetica", size=12),
            wrap="word",
            fg_color=COLOR_BG_CARD_LIGHT,
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=8
        )
        self.txt_politica.pack(fill="both", expand=True, padx=20, pady=(15, 12))
        self.txt_politica.insert("1.0", TEXTO_POLITICA_COMPLETO)
        self.txt_politica.configure(state="disabled")

        # 3. Pie de acciones y consentimiento
        f_footer = ctk.CTkFrame(self, fg_color="transparent")
        f_footer.pack(fill="x", padx=20, pady=(0, 18))

        if self.modo_inicio:
            f_info = ctk.CTkFrame(f_footer, fg_color="transparent")
            f_info.pack(side="left", fill="x", expand=True, padx=(4, 15))

            ctk.CTkLabel(
                f_info,
                text="⚠️ Para acceder a KernossAI debes aceptar de forma expresa la Política de Privacidad.",
                font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                text_color=COLOR_TEXT_MUTED,
                anchor="w"
            ).pack(anchor="w")

            btn_rechazar = ctk.CTkButton(
                f_footer,
                text="❌ No Acepto (Salir)",
                width=160,
                height=40,
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                fg_color="#7f1d1d",
                hover_color="#991b1b",
                command=self._accion_rechazar
            )
            btn_rechazar.pack(side="right", padx=(10, 0))

            btn_aceptar = ctk.CTkButton(
                f_footer,
                text="✅ Acepto los Términos y RGPD",
                width=240,
                height=40,
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                fg_color=COLOR_SUCCESS,
                hover_color="#15803d",
                command=self._accion_aceptar
            )
            btn_aceptar.pack(side="right")
        else:
            ctk.CTkButton(
                f_footer,
                text="Entendido y Cerrar",
                width=160,
                height=38,
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                fg_color=COLOR_ACCENT_PRIMARY,
                hover_color=COLOR_ACCENT_HOVER,
                command=self.destroy
            ).pack(side="right")

    def _accion_aceptar(self):
        registrar_aceptacion_politica()
        if self.on_aceptar:
            self.on_aceptar()
        self.destroy()

    def _accion_rechazar(self):
        if self.on_rechazar:
            self.on_rechazar()
        else:
            try:
                messagebox.showinfo(
                    "Política No Aceptada",
                    "Al no aceptar la Política de Privacidad y el tratamiento legítimo de datos para seguridad técnica, no es posible utilizar KernossAI.\n\nLa aplicación se cerrará."
                )
            except Exception:
                pass
            sys.exit(0)


class VentanaConsentimientoInicial(ctk.CTk, _BasePoliticaUI):
    """Ventana raíz primaria mostrada al abrir la app cuando aún no se ha aceptado la política."""

    def __init__(self, on_aceptar=None, on_rechazar=None):
        super().__init__()
        self.title("📜 Política de Privacidad, Aviso Legal y RGPD — KernossAI")
        self.geometry("860x700")
        self.minsize(720, 540)
        self.protocol("WM_DELETE_WINDOW", self._accion_rechazar)

        aplicar_icono(self)
        self._construir_contenido_politica(modo_inicio=True, on_aceptar=on_aceptar, on_rechazar=on_rechazar)
        centrar_ventana(self, 860, 700)


class VentanaPoliticaPrivacidad(ctk.CTkToplevel, _BasePoliticaUI):
    """Ventana modal de Política de Privacidad y RGPD para visualización dentro de la aplicación."""

    def __new__(cls, parent=None, modo_inicio: bool = False, on_aceptar=None, on_rechazar=None):
        # Si no hay ventana padre activa o estamos en modo arranque inicial, crear ventana raíz CTk
        if parent is None or modo_inicio:
            return VentanaConsentimientoInicial(on_aceptar=on_aceptar, on_rechazar=on_rechazar)
        return super().__new__(cls)

    def __init__(self, parent=None, modo_inicio: bool = False, on_aceptar=None, on_rechazar=None):
        super().__init__(parent)
        self.title("📜 Política de Privacidad, Aviso Legal y RGPD — KernossAI")
        self.geometry("860x700")
        self.minsize(720, 540)

        aplicar_icono(self)
        self._construir_contenido_politica(modo_inicio=modo_inicio, on_aceptar=on_aceptar, on_rechazar=on_rechazar)
        centrar_ventana(self, 860, 700)

        if parent:
            try:
                self.transient(parent)
            except Exception:
                pass
        try:
            self.after(80, self.grab_set)
        except Exception:
            pass
