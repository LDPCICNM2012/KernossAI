"""
KernossAI - Ventana de Acceso y Registro
Módulo de autenticación con selección reactiva de idioma y control de acceso.
"""

import re
import customtkinter as ctk
from KernossAI.core.theme import (
    COLOR_BG_DARK,
    COLOR_BG_CARD,
    COLOR_BG_CARD_LIGHT,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_CYAN_HOVER,
    COLOR_ACCENT_SKY,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_DANGER,
    centrar_ventana,
    aplicar_icono,
)
from KernossAI.core.auth import login, registro
from KernossAI.core.config import obtener_idioma, guardar_idioma
from KernossAI.core.i18n import t, fijar_idioma, IDIOMAS_DISPONIBLES, obtener_idioma_activo
from KernossAI.ui.login.home_alert import VentanaConfirmacionHogar


class PantallaLogin(ctk.CTk):
    """Ventana principal de inicio de sesión y registro de usuarios."""
    def __init__(self):
        super().__init__()
        self.title("KernossAI – Acceso")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG_DARK)
        self.usuario_autenticado = None
        aplicar_icono(self)
        centrar_ventana(self, 520, 680)
        self._build_ui()

    def _al_cambiar_idioma(self, nombre_idioma: str):
        for code, name in IDIOMAS_DISPONIBLES.items():
            if name == nombre_idioma:
                fijar_idioma(code)
                guardar_idioma(code)
                break
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()

    def _build_ui(self):
        # Barra superior con Selector de Idioma
        bar_top_lang = ctk.CTkFrame(self, fg_color="transparent")
        bar_top_lang.pack(fill="x", padx=35, pady=(15, 0))

        ctk.CTkLabel(
            bar_top_lang, text=t("lbl_selecciona_idioma"),
            font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MUTED
        ).pack(side="left")

        idiomas_nombres = list(IDIOMAS_DISPONIBLES.values())
        idioma_actual = IDIOMAS_DISPONIBLES.get(obtener_idioma_activo(), "🇪🇸 Español")

        self.combo_idioma_login = ctk.CTkComboBox(
            bar_top_lang, values=idiomas_nombres,
            font=("Segoe UI", 11), width=150, height=28,
            fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER,
            command=self._al_cambiar_idioma
        )
        self.combo_idioma_login.set(idioma_actual)
        self.combo_idioma_login.pack(side="right")

        # Header institucional
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 15))

        ctk.CTkLabel(header_frame, text=t("app_nombre"),
                     font=("Segoe UI", 36, "bold"), text_color=COLOR_ACCENT_SKY).pack()
        ctk.CTkLabel(header_frame, text=t("app_subtitulo"),
                     font=("Segoe UI", 12), text_color=COLOR_TEXT_MUTED).pack(pady=(2, 0))

        # Tarjeta contenedora de Login
        self.frame = ctk.CTkFrame(self, corner_radius=18, fg_color=COLOR_BG_CARD,
                                  border_width=1, border_color=COLOR_BORDER)
        self.frame.pack(padx=45, fill="x")

        self.tab = ctk.CTkTabview(self.frame, height=340, fg_color=COLOR_BG_CARD_LIGHT,
                                  segmented_button_selected_color=COLOR_ACCENT_PRIMARY,
                                  segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
                                  segmented_button_unselected_color=COLOR_BG_CARD,
                                  segmented_button_unselected_hover_color=COLOR_BG_SURFACE)
        self.tab.pack(fill="x", padx=16, pady=16)
        self.tab.add(t("tab_login"))
        self.tab.add(t("tab_registro"))

        # ── TAB: INICIAR SESIÓN ──
        login_tab = self.tab.tab(t("tab_login"))
        ctk.CTkLabel(login_tab, text=t("lbl_email"), anchor="w", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(fill="x", padx=10, pady=(10, 2))
        self.entry_login_email = ctk.CTkEntry(login_tab, placeholder_text=t("placeholder_email"), height=38,
                                              fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.entry_login_email.pack(fill="x", padx=10)

        ctk.CTkLabel(login_tab, text=t("lbl_pass"), anchor="w", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(fill="x", padx=10, pady=(10, 2))
        self.entry_login_pass = ctk.CTkEntry(login_tab, placeholder_text=t("placeholder_pass"), show="•", height=38,
                                             fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.entry_login_pass.pack(fill="x", padx=10)
        self.entry_login_pass.bind("<Return>", lambda e: self._login())

        ctk.CTkButton(login_tab, text=t("btn_login"), height=42,
                      fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                      font=("Segoe UI", 13, "bold"),
                      command=self._login).pack(fill="x", padx=10, pady=(20, 5))
        self.lbl_login_error = ctk.CTkLabel(login_tab, text="", text_color=COLOR_DANGER, font=("Segoe UI", 11))
        self.lbl_login_error.pack()

        # ── TAB: REGISTRO ──
        reg = self.tab.tab(t("tab_registro"))
        ctk.CTkLabel(reg, text=t("lbl_nombre"), anchor="w", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(fill="x", padx=10, pady=(6, 2))
        self.entry_reg_nombre = ctk.CTkEntry(reg, placeholder_text=t("placeholder_nombre"), height=36,
                                             fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.entry_reg_nombre.pack(fill="x", padx=10)

        ctk.CTkLabel(reg, text=t("lbl_email"), anchor="w", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(fill="x", padx=10, pady=(6, 2))
        self.entry_reg_email = ctk.CTkEntry(reg, placeholder_text=t("placeholder_email"), height=36,
                                            fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.entry_reg_email.pack(fill="x", padx=10)

        ctk.CTkLabel(reg, text=t("lbl_pass"), anchor="w", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(fill="x", padx=10, pady=(6, 2))
        self.entry_reg_pass = ctk.CTkEntry(reg, placeholder_text=t("placeholder_pass_reg"), show="•", height=36,
                                           fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.entry_reg_pass.pack(fill="x", padx=10)

        ctk.CTkLabel(reg, text=t("lbl_rol"), anchor="w", font=("Segoe UI", 12, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(fill="x", padx=10, pady=(6, 2))
        self.combo_rol = ctk.CTkOptionMenu(reg, values=[t("lbl_rol_alumno"), t("lbl_rol_profesor")], height=36,
                                           fg_color=COLOR_ACCENT_PRIMARY,
                                           button_color=COLOR_ACCENT_HOVER,
                                           dropdown_fg_color=COLOR_BG_CARD)
        self.combo_rol.pack(fill="x", padx=10)

        ctk.CTkButton(reg, text=t("btn_registro"), height=40,
                      fg_color=COLOR_ACCENT_CYAN, hover_color=COLOR_ACCENT_CYAN_HOVER,
                      font=("Segoe UI", 13, "bold"),
                      command=self._registrar).pack(fill="x", padx=10, pady=(12, 4))
        self.lbl_reg_error = ctk.CTkLabel(reg, text="", text_color=COLOR_DANGER, font=("Segoe UI", 11))
        self.lbl_reg_error.pack()

        ctk.CTkLabel(self, text=t("login_privacidad"),
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_DIM).pack(pady=(16, 0))

    def _login(self):
        email = self.entry_login_email.get().strip().lower()
        password = self.entry_login_pass.get()
        if not email or not password:
            self.lbl_login_error.configure(text=t("login_error_campos"))
            return
        self.lbl_login_error.configure(text=t("login_conectando"), text_color=COLOR_ACCENT_SKY)
        self.update()
        exito, error, sesion, hogar_info = login(email, password)
        if not exito:
            self.lbl_login_error.configure(text=error, text_color=COLOR_DANGER)
            return

        self.usuario_autenticado = sesion

        if hogar_info.get("hogar_estado") == "fuera_de_hogar":
            def _cerrar_y_entrar():
                self.destroy()
            VentanaConfirmacionHogar(self, hogar_info, on_finalizar=_cerrar_y_entrar)
        else:
            self.destroy()

    def _registrar(self):
        nombre = self.entry_reg_nombre.get().strip()
        email = self.entry_reg_email.get().strip().lower()
        password = self.entry_reg_pass.get()
        rol_txt = self.combo_rol.get()
        rol = "Profesor" if rol_txt in [t("lbl_rol_profesor"), "Profesor", "Teacher", "Lehrer / Dozent"] else "Alumno"

        if not nombre or not email or not password:
            self.lbl_reg_error.configure(text=t("login_error_campos"))
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.lbl_reg_error.configure(text=t("login_error_correo"))
            return
        if len(password) < 6:
            self.lbl_reg_error.configure(text=t("login_error_pass_len"))
            return
        self.lbl_reg_error.configure(text=t("reg_creando"), text_color=COLOR_ACCENT_SKY)
        self.update()
        exito, error, sesion = registro(nombre, email, password, rol)
        if not exito:
            self.lbl_reg_error.configure(text=error, text_color=COLOR_DANGER)
            return
        self.usuario_autenticado = sesion
        self.destroy()
