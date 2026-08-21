"""
KernossAI - Alertas y Modales de Política de Red Hogar
Modal de inicio (período de 15 días de margen) y confirmación de red de estudio.
"""

import customtkinter as ctk
from tkinter import messagebox
from KernossAI.core.theme import (
    COLOR_BG_DARK,
    COLOR_BG_CARD,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_SKY,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_WARNING,
    centrar_ventana,
    aplicar_icono,
)
from KernossAI.core.auth import (
    actualizar_hogar_principal,
    fijar_red_hogar_actual,
    activar_pase_hogar_temporal,
)


class ModalAlertaCasa(ctk.CTkToplevel):
    """Popup centrado y cerrable que aparece al iniciar si no hay casa establecida o está fuera de ella durante los primeros 15 días."""
    def __init__(self, parent, tipo: str = "sin_casa", dias_restantes: int = 15, on_casa_establecida=None):
        super().__init__(parent)
        self.parent = parent
        self.tipo = tipo
        self.dias_restantes = dias_restantes
        self.on_casa_establecida = on_casa_establecida
        
        self.title("🏡 Configuración de Red Hogar — KernossAI")
        self.geometry("540x370")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        aplicar_icono(self)
        centrar_ventana(self, 540, 370)
        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=14, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        if self.tipo == "sin_casa":
            icono = "🏡"
            titulo = "No hay casa establecida"
            subtitulo = f"Te quedan {self.dias_restantes} días de margen desde la instalación."
            color_icono = COLOR_ACCENT_SKY
        else:
            icono = "⚠️"
            titulo = "Conexión fuera de tu Hogar Principal"
            subtitulo = f"Te quedan {self.dias_restantes} días de período inicial antes del bloqueo."
            color_icono = COLOR_WARNING

        f_hdr = ctk.CTkFrame(card, fg_color="transparent")
        f_hdr.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(f_hdr, text=icono, font=("Segoe UI", 28)).pack(side="left", padx=(0, 10))

        f_txts = ctk.CTkFrame(f_hdr, fg_color="transparent")
        f_txts.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(f_txts, text=titulo, font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x")
        ctk.CTkLabel(f_txts, text=subtitulo, font=("Segoe UI", 10, "bold"), text_color=color_icono, anchor="w").pack(fill="x")

        # Separador
        ctk.CTkFrame(card, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=18, pady=(4, 10))

        # Mensaje explicativo
        if self.tipo == "sin_casa":
            cuerpo = (
                "No has registrado tu red de Hogar Principal de Estudio aún.\n\n"
                f"• Puedes usar KernossAI normalmente durante los 15 días posteriores a la instalación (quedan {self.dias_restantes} días).\n"
                "• A partir del día 15, todos los servicios y módulos quedarán cerrados hasta que establezcas tu casa."
            )
        else:
            cuerpo = (
                "Estás conectado a una red diferente a tu Hogar Principal de Estudio.\n\n"
                f"• Período de gracia restante: {self.dias_restantes} días.\n"
                "• Al vencer el plazo de 15 días, el acceso fuera de casa requerirá activar el pase temporal de 7 días "
                "(disponible 1 vez al mes) o registrar esta red como tu casa."
            )

        ctk.CTkLabel(card, text=cuerpo, font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED,
                     wraplength=470, justify="left").pack(fill="x", padx=18, pady=(0, 12))

        # Botones de acción
        f_btns = ctk.CTkFrame(card, fg_color="transparent")
        f_btns.pack(fill="x", padx=18, pady=(0, 10))

        btn_establecer = ctk.CTkButton(
            f_btns, text="🏡 Establecer Esta Red como mi Casa", height=38,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_SUCCESS, hover_color="#15803d",
            command=self._establecer_casa
        )
        btn_establecer.pack(fill="x", pady=(0, 6))

        if self.tipo != "sin_casa":
            btn_temporal = ctk.CTkButton(
                f_btns, text="✈️ Activar Hogar Temporal (7 Días)", height=32,
                font=("Segoe UI", 10, "bold"), fg_color="#1e1b4b", border_width=1, border_color="#818cf8",
                text_color="#e0e7ff", hover_color="#4338ca",
                command=self._activar_temporal
            )
            btn_temporal.pack(fill="x", pady=(0, 6))

        btn_cerrar = ctk.CTkButton(
            f_btns, text="Cerrar y Continuar", height=28,
            font=("Segoe UI", 10), fg_color="transparent", text_color=COLOR_TEXT_MUTED,
            hover_color=COLOR_BG_SURFACE,
            command=self.destroy
        )
        btn_cerrar.pack(fill="x")

    def _establecer_casa(self):
        email = getattr(self.parent, "email", None) or getattr(self.parent, "sesion", {}).get("email", "")
        ok, msg = fijar_red_hogar_actual(email=email)
        if ok:
            messagebox.showinfo("Casa Establecida", msg)
            if self.on_casa_establecida:
                self.on_casa_establecida()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

    def _activar_temporal(self):
        email = getattr(self.parent, "email", None) or getattr(self.parent, "sesion", {}).get("email", "")
        ok, msg = activar_pase_hogar_temporal(email=email)
        if ok:
            messagebox.showinfo("Pase Temporal Activo", msg)
            if self.on_casa_establecida:
                self.on_casa_establecida()
            self.destroy()
        else:
            messagebox.showwarning("Aviso", msg)


class VentanaConfirmacionHogar(ctk.CTkToplevel):
    """Modal estilo Netflix para confirmar ubicación/red principal de estudio."""
    def __init__(self, parent, hogar_info: dict, on_finalizar):
        super().__init__(parent)
        self.title("🏠 Hogar Principal de Estudio – KernossAI")
        self.geometry("580x480")
        self.minsize(520, 420)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        self.grab_set()
        aplicar_icono(self)
        centrar_ventana(self, 580, 480)
        self.hogar_info = hogar_info
        self.on_finalizar = on_finalizar
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(22, 10))

        ctk.CTkLabel(header, text="🏠 ¿Estás en tu Hogar Principal?",
                     font=("Segoe UI", 20, "bold"), text_color=COLOR_ACCENT_SKY).pack(anchor="w")
        ctk.CTkLabel(header, text="Control de ubicación y protección de cuenta compartida",
                     font=("Segoe UI", 12), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        card = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=14,
                            border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="both", expand=True, padx=25, pady=(5, 15))

        nombre_hogar = self.hogar_info.get("hogar_nombre", "Hogar Principal")
        ip_actual = self.hogar_info.get("ip_actual", "Nueva Red")

        ctk.CTkLabel(card, text="📍 Ubicación o Red No Habitual Detectada",
                     font=("Segoe UI", 14, "bold"), text_color=COLOR_WARNING).pack(anchor="w", padx=18, pady=(16, 6))

        desc = (
            f"Tu cuenta de KernossAI tiene registrado como Hogar Principal: '{nombre_hogar}'.\n\n"
            f"Hemos detectado que estás iniciando sesión desde una red o ubicación diferente ({ip_actual}). "
            "Para evitar el uso compartido indebido y proteger tu cuenta:\n\n"
            "• Si estás en la biblioteca, cafetería o de viaje, puedes continuar normalmente.\n"
            "• Si te has mudado o esta es tu nueva red fija, puedes actualizar tu Hogar Principal."
        )
        ctk.CTkLabel(card, text=desc, font=("Segoe UI", 12), text_color=COLOR_TEXT_MAIN,
                     wraplength=480, justify="left").pack(anchor="w", padx=18, pady=(0, 15))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkButton(
            btns, text="✈️ Estudiar Fuera de Casa (De viaje)",
            height=40, font=("Segoe UI", 12, "bold"),
            fg_color=COLOR_BG_SURFACE, hover_color=COLOR_BORDER,
            command=self._continuar_temporal
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btns, text="🏡 Establecer Esta Red como mi Hogar Principal",
            height=40, font=("Segoe UI", 12, "bold"),
            fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
            command=self._actualizar_hogar
        ).pack(fill="x")

    def _continuar_temporal(self):
        self.destroy()
        if self.on_finalizar:
            self.on_finalizar()

    def _actualizar_hogar(self):
        exito, msg = actualizar_hogar_principal("Hogar Principal de Estudio")
        if exito:
            messagebox.showinfo("Hogar Actualizado", "Se ha registrado esta red como tu Hogar Principal de Estudio.")
        self.destroy()
        if self.on_finalizar:
            self.on_finalizar()
