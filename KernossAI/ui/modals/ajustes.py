"""
KernossAI - Ventana de Ajustes y Preferencias del Sistema
Configuración de idioma, roles, gestión de multicuentas, motor de voz TTS y red del Hogar.
"""

import threading
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
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    aplicar_icono,
    centrar_ventana,
)
from KernossAI.core.config import (
    obtener_idioma,
    guardar_idioma,
    obtener_ajustes_tts,
    guardar_ajustes_tts,
    obtener_pase_temporal,
    guardar_activacion_pase_temporal,
)
from KernossAI.core.i18n import t, fijar_idioma, IDIOMAS_DISPONIBLES
from KernossAI.core.tts import tts_engine, VOICES_DISPONIBLES, VELOCIDADES_DISPONIBLES
from KernossAI.core.auth import (
    obtener_cuentas_guardadas,
    cambiar_a_cuenta,
    eliminar_cuenta_switcher,
    agregar_cuenta_secundaria,
    actualizar_rol_usuario,
    obtener_estado_casa,
    fijar_red_hogar_actual,
    activar_pase_hogar_temporal,
    borrar_cuenta_usuario,
)


class ModalAgregarCuenta(ctk.CTkToplevel):
    """Modal para iniciar sesión con una cuenta adicional y añadirla al switcher."""
    def __init__(self, parent, on_cuenta_agregada):
        super().__init__(parent)
        self.title("👥 Iniciar Sesión con Otra Cuenta — KernossAI")
        self.geometry("450x380")
        self.minsize(400, 340)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        self.grab_set()
        self.on_cuenta_agregada = on_cuenta_agregada
        aplicar_icono(self)
        centrar_ventana(self, 450, 380)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="👥 Iniciar Sesión con Otra Cuenta", font=("Segoe UI", 16, "bold"), text_color=COLOR_ACCENT_SKY).pack(padx=20, pady=(20, 4))
        ctk.CTkLabel(self, text="Agrega una cuenta adicional para alternar entre ellas sin cerrar sesión.", font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED).pack(padx=20, pady=(0, 15))

        f_card = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        f_card.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        ctk.CTkLabel(f_card, text="Correo Electrónico:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=16, pady=(12, 2))
        self.entry_email = ctk.CTkEntry(f_card, height=36, font=("Segoe UI", 11), placeholder_text="ej: usuario@correo.com")
        self.entry_email.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(f_card, text="Contraseña:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=16, pady=(0, 2))
        self.entry_pass = ctk.CTkEntry(f_card, height=36, font=("Segoe UI", 11), show="•", placeholder_text="••••••••")
        self.entry_pass.pack(fill="x", padx=16, pady=(0, 10))
        self.entry_pass.bind("<Return>", lambda e: self._guardar())

        self.lbl_estado = ctk.CTkLabel(f_card, text="", font=("Segoe UI", 10))
        self.lbl_estado.pack(anchor="w", padx=16, pady=(0, 6))

        f_btns = ctk.CTkFrame(self, fg_color="transparent")
        f_btns.pack(fill="x", padx=20, pady=(0, 18))

        self.btn_guardar = ctk.CTkButton(f_btns, text="➕ Agregar Cuenta", height=38, font=("Segoe UI", 11, "bold"),
                                          fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER, command=self._guardar)
        self.btn_guardar.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(f_btns, text="Cancelar", height=38, width=85, font=("Segoe UI", 11),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_BORDER, command=self.destroy).pack(side="right")

    def _guardar(self):
        email = self.entry_email.get().strip().lower()
        password = self.entry_pass.get()
        if not email or not password:
            self.lbl_estado.configure(text="Completa todos los campos.", text_color=COLOR_DANGER)
            return

        self.lbl_estado.configure(text="⏳ Verificando credenciales...", text_color=COLOR_ACCENT_SKY)
        self.btn_guardar.configure(state="disabled")

        def _thread():
            ok, msg, _ = agregar_cuenta_secundaria(email, password)
            if ok:
                def _exito():
                    if self.on_cuenta_agregada:
                        self.on_cuenta_agregada()
                    self.destroy()
                    messagebox.showinfo("Cuenta Agregada", f"La cuenta '{email}' se ha guardado en el gestor de multicuentas.")
                self.after(0, _exito)
            else:
                def _error():
                    self.lbl_estado.configure(text=msg, text_color=COLOR_DANGER)
                    self.btn_guardar.configure(state="normal")
                self.after(0, _error)

        threading.Thread(target=_thread, daemon=True).start()


class VentanaAjustes(ctk.CTkToplevel):
    """Ventana de configuración, idioma, preferencias de voz TTS y estado de Hogar."""
    def __init__(self, master):
        super().__init__(master)
        self.title(t("ajustes_titulo"))
        self.geometry("620x740")
        self.minsize(540, 600)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(master)
        self.grab_set()
        aplicar_icono(self)
        centrar_ventana(self, 620, 740)
        
        self.sesion_actual = getattr(master, "sesion", {})
        self.email_actual = self.sesion_actual.get("email", "").lower()
        self.rol_original = self.sesion_actual.get("rol", "Alumno")
        
        self._build_ui()

    def _build_ui(self):
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=25, pady=(18, 8))

        ctk.CTkLabel(frame_header, text=t("ajustes_titulo"),
                     font=("Segoe UI", 20, "bold"), text_color=COLOR_ACCENT_SKY).pack(anchor="w")
        ctk.CTkLabel(frame_header, text=t("ajustes_subtitulo"),
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        self.scroll_tarjeta = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_CARD, corner_radius=14,
                                                     border_width=1, border_color=COLOR_BORDER)
        self.scroll_tarjeta.pack(fill="both", expand=True, padx=25, pady=(5, 12))

        # 1. Idioma
        ctk.CTkLabel(self.scroll_tarjeta, text=f"🌐 {t('ajustes_sec_idioma')}:",
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=18, pady=(12, 4))
        
        self.map_idiomas_a_id = {v: k for k, v in IDIOMAS_DISPONIBLES.items()}
        nombres_idiomas = list(IDIOMAS_DISPONIBLES.values())
        idioma_actual = obtener_idioma()
        nombre_idioma_actual = IDIOMAS_DISPONIBLES.get(idioma_actual, nombres_idiomas[0])

        self.combo_idioma = ctk.CTkComboBox(self.scroll_tarjeta, values=nombres_idiomas, height=36,
                                             font=("Segoe UI", 12), fg_color=COLOR_BG_CARD_LIGHT,
                                             border_color=COLOR_BORDER)
        self.combo_idioma.set(nombre_idioma_actual)
        self.combo_idioma.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkFrame(self.scroll_tarjeta, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=18, pady=(2, 10))

        # 2. Rol
        ctk.CTkLabel(self.scroll_tarjeta, text="🎓 Modo de Cuenta / Rol Académico:",
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=18, pady=(0, 2))
        ctk.CTkLabel(self.scroll_tarjeta, text="Elige entre 'Alumno' (estudio) o 'Profesor' (herramientas docentes).",
                     font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 4))

        roles_disp = ["Alumno", "Profesor"]
        rol_activo = self.rol_original if self.rol_original in roles_disp else "Alumno"

        self.combo_rol = ctk.CTkComboBox(self.scroll_tarjeta, values=roles_disp, height=36,
                                         font=("Segoe UI", 12), fg_color=COLOR_BG_CARD_LIGHT,
                                         border_color=COLOR_BORDER)
        self.combo_rol.set(rol_activo)
        self.combo_rol.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkFrame(self.scroll_tarjeta, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=18, pady=(2, 10))

        # 3. Multicuentas
        ctk.CTkLabel(self.scroll_tarjeta, text="👥 Gestión de Multicuentas (Alternar Cuentas):",
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=18, pady=(0, 2))
        ctk.CTkLabel(self.scroll_tarjeta, text="Inicia sesión con varias cuentas y cambia de una a otra al instante.",
                     font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 6))

        self.frame_multicuentas_lista = ctk.CTkFrame(self.scroll_tarjeta, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.frame_multicuentas_lista.pack(fill="x", padx=18, pady=(0, 8))

        self._cargar_multicuentas()

        self.btn_add_cuenta = ctk.CTkButton(
            self.scroll_tarjeta, text="➕ Iniciar Sesión con Otra Cuenta",
            font=("Segoe UI", 11, "bold"), height=32,
            fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
            command=self._abrir_modal_agregar_cuenta
        )
        self.btn_add_cuenta.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkFrame(self.scroll_tarjeta, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=18, pady=(2, 10))

        # 4. Lector de voz TTS
        ctk.CTkLabel(self.scroll_tarjeta, text=f"🔊 {t('ajustes_sec_voz')} - {t('ajustes_lbl_voz')}",
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=18, pady=(0, 4))

        voz_actual, vel_actual = obtener_ajustes_tts()

        self.map_voces_a_id = {v: k for k, v in VOICES_DISPONIBLES.items()}
        nombres_voces = list(VOICES_DISPONIBLES.values())
        nombre_voz_actual = VOICES_DISPONIBLES.get(voz_actual, nombres_voces[0])

        self.combo_voz = ctk.CTkComboBox(self.scroll_tarjeta, values=nombres_voces, height=36,
                                         font=("Segoe UI", 12), fg_color=COLOR_BG_CARD_LIGHT,
                                         border_color=COLOR_BORDER)
        self.combo_voz.set(nombre_voz_actual)
        self.combo_voz.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkLabel(self.scroll_tarjeta, text=f"⚡ {t('ajustes_lbl_velocidad')}",
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=18, pady=(0, 4))

        self.map_vel_a_id = {v: k for k, v in VELOCIDADES_DISPONIBLES.items()}
        nombres_vel = list(VELOCIDADES_DISPONIBLES.values())
        nombre_vel_actual = VELOCIDADES_DISPONIBLES.get(vel_actual, nombres_vel[1])

        self.combo_vel = ctk.CTkComboBox(self.scroll_tarjeta, values=nombres_vel, height=36,
                                         font=("Segoe UI", 12), fg_color=COLOR_BG_CARD_LIGHT,
                                         border_color=COLOR_BORDER)
        self.combo_vel.set(nombre_vel_actual)
        self.combo_vel.pack(fill="x", padx=18, pady=(0, 10))

        self.btn_probar = ctk.CTkButton(self.scroll_tarjeta, text=t("ajustes_btn_probar"),
                                        font=("Segoe UI", 11, "bold"), height=32,
                                        fg_color=COLOR_BG_SURFACE, border_width=1, border_color=COLOR_ACCENT_CYAN,
                                        hover_color=COLOR_ACCENT_PRIMARY,
                                        command=self._probar_voz)
        self.btn_probar.pack(fill="x", padx=18, pady=(0, 10))

        ctk.CTkFrame(self.scroll_tarjeta, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=18, pady=(2, 10))

        # 5. Red Hogar
        ctk.CTkLabel(self.scroll_tarjeta, text="🏡 Red y Ubicación de Estudio — Estado de Casa:",
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=18, pady=(0, 2))
        ctk.CTkLabel(self.scroll_tarjeta, text="Indica si te encuentras en tu red doméstica principal de estudio para la sincronización y protección de cuenta.",
                     font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 6))

        card_casa = ctk.CTkFrame(self.scroll_tarjeta, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card_casa.pack(fill="x", padx=18, pady=(0, 10))

        row_casa_header = ctk.CTkFrame(card_casa, fg_color="transparent")
        row_casa_header.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(row_casa_header, text="Estado de Red:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

        self.lbl_badge_casa = ctk.CTkLabel(
            row_casa_header, text="  Casa: ⏳ Comprobando...  ",
            font=("Segoe UI", 11, "bold"), corner_radius=6,
            fg_color=COLOR_BG_CARD, text_color=COLOR_TEXT_MUTED
        )
        self.lbl_badge_casa.pack(side="right")

        self.lbl_detalles_casa = ctk.CTkLabel(
            card_casa, text="Verificando IP pública y red de hogar...",
            font=("Segoe UI", 9), text_color=COLOR_TEXT_MUTED, justify="left", wraplength=480
        )
        self.lbl_detalles_casa.pack(anchor="w", padx=14, pady=(0, 8))

        row_casa_actions = ctk.CTkFrame(card_casa, fg_color="transparent")
        row_casa_actions.pack(fill="x", padx=14, pady=(0, 6))

        self.btn_fijar_casa = ctk.CTkButton(
            row_casa_actions, text="🏡 Establecer Esta Red como mi Casa",
            font=("Segoe UI", 10, "bold"), height=30,
            fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
            command=self._fijar_red_casa_actual
        )
        self.btn_fijar_casa.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_refrescar_casa = ctk.CTkButton(
            row_casa_actions, text="🔄 Comprobar",
            font=("Segoe UI", 10, "bold"), height=30, width=95,
            fg_color=COLOR_BG_CARD, hover_color=COLOR_BORDER,
            command=self._comprobar_estado_casa
        )
        self.btn_refrescar_casa.pack(side="right")

        row_casa_temp = ctk.CTkFrame(card_casa, fg_color="transparent")
        row_casa_temp.pack(fill="x", padx=14, pady=(0, 10))

        self.btn_activar_temp = ctk.CTkButton(
            row_casa_temp, text="✈️ Establecer Casa solo por 7 Días (Modo Viaje • 1 vez al mes)",
            font=("Segoe UI", 10, "bold"), height=30,
            fg_color="#1e1b4b", border_width=1, border_color="#818cf8",
            text_color="#e0e7ff", hover_color="#4338ca",
            command=self._activar_casa_temporal_7dias
        )
        self.btn_activar_temp.pack(fill="x")

        self._comprobar_estado_casa()

        ctk.CTkFrame(self.scroll_tarjeta, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=18, pady=(2, 10))

        # 6. Borrar Cuenta
        ctk.CTkLabel(self.scroll_tarjeta, text="⚠️ Zona de Privacidad — Cuenta",
                     font=("Segoe UI", 11, "bold"), text_color=COLOR_DANGER).pack(anchor="w", padx=18, pady=(0, 1))

        ctk.CTkLabel(self.scroll_tarjeta, text="Elimina de forma permanente tu usuario, historial y acceso del servidor.",
                     font=("Segoe UI", 9), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=18, pady=(0, 6))

        self.btn_eliminar_cuenta = ctk.CTkButton(
            self.scroll_tarjeta, text="🗑️ Borrar Mi Cuenta Definitivamente",
            font=("Segoe UI", 11, "bold"), height=34,
            fg_color="#7f1d1d", hover_color="#991b1b",
            border_width=1, border_color=COLOR_DANGER,
            command=self._solicitar_eliminar_cuenta
        )
        self.btn_eliminar_cuenta.pack(fill="x", padx=18, pady=(0, 12))

        # Botones inferiores
        frame_btns = ctk.CTkFrame(self, fg_color="transparent")
        frame_btns.pack(fill="x", padx=25, pady=(0, 18))

        ctk.CTkButton(frame_btns, text=t("ajustes_btn_guardar"), height=40,
                      font=("Segoe UI", 12, "bold"),
                      fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                      command=self._guardar).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(frame_btns, text=t("ajustes_btn_cancelar"), height=40, width=90,
                      font=("Segoe UI", 12),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_BORDER,
                      command=self._cerrar).pack(side="right")

    def _cargar_multicuentas(self):
        for w in self.frame_multicuentas_lista.winfo_children():
            w.destroy()

        cuentas = obtener_cuentas_guardadas()
        if not cuentas and self.email_actual:
            cuentas = [{
                "email": self.email_actual,
                "nombre": self.sesion_actual.get("nombre", "Usuario"),
                "rol": self.sesion_actual.get("rol", "Alumno")
            }]

        for c in cuentas:
            em = c.get("email", "").lower()
            nom = c.get("nombre", em)
            rol = c.get("rol", "Alumno")
            es_activa = (em == self.email_actual)

            row = ctk.CTkFrame(self.frame_multicuentas_lista, fg_color=COLOR_BG_CARD if es_activa else "transparent", corner_radius=6)
            row.pack(fill="x", padx=6, pady=3)

            badge = "🟢 (Activa)" if es_activa else "👤"
            ctk.CTkLabel(row, text=f"{badge} {nom} ({em}) — {rol}", font=("Segoe UI", 10, "bold" if es_activa else "normal"),
                         text_color=COLOR_ACCENT_SKY if es_activa else COLOR_TEXT_MAIN).pack(side="left", padx=8, pady=6)

            if not es_activa:
                ctk.CTkButton(row, text="🗑️", width=30, height=26, font=("Segoe UI", 10),
                              fg_color="transparent", hover_color=COLOR_DANGER_HOVER, text_color=COLOR_TEXT_MUTED,
                              command=lambda e=em: self._quitar_cuenta_switcher(e)).pack(side="right", padx=(2, 6), pady=4)

                ctk.CTkButton(row, text="🔄 Cambiar", width=80, height=26, font=("Segoe UI", 10, "bold"),
                              fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                              command=lambda e=em: self._switch_to_account(e)).pack(side="right", padx=2, pady=4)

    def _abrir_modal_agregar_cuenta(self):
        ModalAgregarCuenta(self, on_cuenta_agregada=self._cargar_multicuentas)

    def _switch_to_account(self, email):
        ok, msg, nueva_sesion = cambiar_a_cuenta(email)
        if ok:
            messagebox.showinfo("Sesión Cambiada", f"Has cambiado a la cuenta de: {nueva_sesion.get('nombre', email)}")
            self._cerrar()
            if hasattr(self.master, "_al_cambiar_cuenta"):
                self.master._al_cambiar_cuenta(nueva_sesion)
        else:
            messagebox.showerror("Error", msg)

    def _quitar_cuenta_switcher(self, email):
        eliminar_cuenta_switcher(email)
        self._cargar_multicuentas()

    def _comprobar_estado_casa(self):
        if not hasattr(self, "lbl_badge_casa"):
            return
        self.lbl_badge_casa.configure(text="  Casa: ⏳ Comprobando...  ", fg_color=COLOR_BG_CARD, text_color=COLOR_TEXT_MUTED)
        
        def _thread():
            codigo, texto, detalles = obtener_estado_casa(self.email_actual)
            
            def _render():
                if not hasattr(self, "lbl_badge_casa") or not self.winfo_exists():
                    return
                ip_act = detalles.get("ip_actual", "N/D")
                ip_hog = detalles.get("hogar_ip", "Sin registrar")
                dias_rest = detalles.get("dias_restantes_pase", 0)
                fecha_disp = detalles.get("fecha_disp_pase", "Disponible")
                dias_falta = detalles.get("dias_para_disp", 0)
                
                if codigo == "si":
                    self.lbl_badge_casa.configure(text="  Casa: 🟢 SI  ", fg_color="#10b981", text_color="#ffffff")
                    self.lbl_detalles_casa.configure(text=f"✅ Conectado en tu Hogar Principal de Estudio.\n🌐 IP Actual: {ip_act}  |  🏡 IP Hogar: {ip_hog}")
                elif codigo == "si_temporal":
                    self.lbl_badge_casa.configure(text=f"  Casa: 🟢 SI (Temporal {dias_rest}d)  ", fg_color="#059669", text_color="#ffffff")
                    self.lbl_detalles_casa.configure(text=f"✈️ Pase de Hogar Temporal de 7 días activo ({dias_rest} días restantes).\n🌐 IP Actual: {ip_act}  |  🏡 IP Hogar: {ip_hog}")
                elif codigo == "no":
                    self.lbl_badge_casa.configure(text="  Casa: 🔴 NO  ", fg_color="#ef4444", text_color="#ffffff")
                    info_disp = "Pase temporal disponible ahora" if dias_falta == 0 else f"Pase temporal disponible el {fecha_disp}"
                    self.lbl_detalles_casa.configure(text=f"⚠️ Conexión fuera de tu Hogar Principal (Modo viaje / red externa).\n🌐 IP Actual: {ip_act}  |  🏡 IP Hogar: {ip_hog}\n✈️ {info_disp}")
                else:
                    self.lbl_badge_casa.configure(text="  Casa: 🟠 No se sabe  ", fg_color="#f59e0b", text_color="#000000")
                    self.lbl_detalles_casa.configure(text=f"ℹ️ Aún no has registrado una red como Hogar Principal fijo.\n🌐 IP Actual: {ip_act}  |  Pulsa abajo para fijar esta red como tu Casa.")
                    
            self.after(0, _render)
            
        threading.Thread(target=_thread, daemon=True).start()

    def _fijar_red_casa_actual(self):
        def _thread():
            ok, msg = fijar_red_hogar_actual(self.email_actual)
            if ok:
                self.after(0, lambda: messagebox.showinfo("Hogar Principal", msg))
                self.after(0, self._comprobar_estado_casa)
                if hasattr(self.master, "_desbloquear_dashboard"):
                    self.after(0, self.master._desbloquear_dashboard)
            else:
                self.after(0, lambda: messagebox.showerror("Error", msg))
        threading.Thread(target=_thread, daemon=True).start()

    def _activar_casa_temporal_7dias(self):
        activo, dias_rest, fecha_disp, dias_falta = obtener_pase_temporal(self.email_actual)
        if dias_falta > 0 and not activo:
            messagebox.showwarning(
                "Límite Mensual Alcanzado",
                f"Solo puedes activar el Hogar Temporal de 7 días 1 vez al mes.\n\n"
                f"📅 Próxima fecha disponible: {fecha_disp} (en {dias_falta} días)."
            )
            return

        confirm = messagebox.askyesno(
            "✈️ Activar Hogar Temporal por 7 Días",
            "¿Deseas activar el pase de Hogar Temporal por 7 días?\n\n"
            "• Te permitirá utilizar todos los servicios de KernossAI fuera de tu casa durante 7 días continuos.\n"
            "• Recuerda que esta opción solo se puede activar 1 vez al mes (cada 30 días).\n\n"
            "¿Deseas activarlo ahora?"
        )
        if not confirm:
            return

        def _thread():
            ok, msg = activar_pase_hogar_temporal(self.email_actual)
            if ok:
                self.after(0, lambda: messagebox.showinfo("Hogar Temporal Activo", msg))
                self.after(0, self._comprobar_estado_casa)
                if hasattr(self.master, "_desbloquear_dashboard"):
                    self.after(0, self.master._desbloquear_dashboard)
            else:
                self.after(0, lambda: messagebox.showerror("Error", msg))

        threading.Thread(target=_thread, daemon=True).start()

    def _probar_voz(self):
        nombre_voz = self.combo_voz.get()
        voz_id = self.map_voces_a_id.get(nombre_voz, "es-ES-AlvaroNeural")
        nombre_vel = self.combo_vel.get()
        vel_id = self.map_vel_a_id.get(nombre_vel, "+0%")

        guardar_ajustes_tts(voz_id, vel_id)

        if tts_engine.esta_reproduciendo():
            tts_engine.detener()
            self.btn_probar.configure(text=t("ajustes_btn_probar"), fg_color=COLOR_BG_SURFACE)
            return

        def _callback(reproduciendo):
            if reproduciendo:
                self.btn_probar.configure(text="⏹️ Detener Prueba", fg_color=COLOR_DANGER)
            else:
                self.btn_probar.configure(text=t("ajustes_btn_probar"), fg_color=COLOR_BG_SURFACE)

        frases_prueba = {
            "es": "Hola, esta es una prueba de la voz del asistente en KernossAI. ¿Qué te parece?",
            "en": "Hello, this is a test of the assistant voice in KernossAI. How does it sound?",
            "de": "Hallo, dies ist ein Test der KI-Stimme in KernossAI. Wie gefällt sie dir?",
            "fr": "Bonjour, ceci est un test de la voix de l'assistant dans KernossAI. Qu'en pensez-vous ?"
        }
        idioma = obtener_idioma()
        frase = frases_prueba.get(idioma, frases_prueba["es"])

        tts_engine.hablar(frase, callback_estado=lambda r: self.after(0, lambda: _callback(r)))

    def _guardar(self):
        nombre_idioma = self.combo_idioma.get()
        idioma_id = self.map_idiomas_a_id.get(nombre_idioma, "es")
        idioma_anterior = obtener_idioma()
        guardar_idioma(idioma_id)
        fijar_idioma(idioma_id)

        nuevo_rol = self.combo_rol.get()
        if nuevo_rol != self.rol_original:
            ok_rol, _ = actualizar_rol_usuario(nuevo_rol)
            if ok_rol:
                if hasattr(self.master, "sesion"):
                    self.master.sesion["rol"] = nuevo_rol
                if hasattr(self.master, "_al_cambiar_cuenta"):
                    self.master._al_cambiar_cuenta(self.master.sesion)

        nombre_voz = self.combo_voz.get()
        voz_id = self.map_voces_a_id.get(nombre_voz, "es-ES-AlvaroNeural")
        nombre_vel = self.combo_vel.get()
        vel_id = self.map_vel_a_id.get(nombre_vel, "+0%")
        guardar_ajustes_tts(voz_id, vel_id)

        if idioma_id != idioma_anterior:
            if hasattr(self.master, "_recargar_idioma_ui"):
                self.master._recargar_idioma_ui()
            messagebox.showinfo(t("ajustes_titulo"), t("ajustes_aviso_reinicio"))
        else:
            messagebox.showinfo(t("ajustes_titulo"), t("ajustes_guardado_ok"))
        self._cerrar()

    def _solicitar_eliminar_cuenta(self):
        confirm = messagebox.askyesno(
            "⚠️ Eliminar Cuenta",
            "¿Estás seguro de que deseas ELIMINAR tu cuenta de KernossAI?\n\n"
            "• Tu usuario y contraseña se borrarán de Supabase.\n"
            "• Se eliminarán todos tus chats y registros.\n"
            "• Esta acción es IRREVERSIBLE.\n\n"
            "¿Deseas continuar?"
        )
        if not confirm:
            return

        def _thread():
            ok, msg = borrar_cuenta_usuario()
            if ok:
                def _exito():
                    messagebox.showinfo("Cuenta Eliminada", "Tu cuenta ha sido eliminada con éxito del sistema.")
                    self._cerrar()
                    if hasattr(self.master, "_cerrar_sesion"):
                        self.master._cerrar_sesion()
                    else:
                        self.master.destroy()
                self.after(0, _exito)
            else:
                self.after(0, lambda: messagebox.showerror("Error", msg))

        threading.Thread(target=_thread, daemon=True).start()

    def _cerrar(self):
        tts_engine.detener()
        self.destroy()
