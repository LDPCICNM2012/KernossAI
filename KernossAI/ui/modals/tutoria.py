"""
KernossAI - Módulo de Tutoría y Vinculación Alumno-Profesor
Sistema de vinculación académica, solicitudes y chat directo cifrado E2EE.
"""

import threading
import customtkinter as ctk
from tkinter import messagebox
from KernossAI.core.theme import (
    COLOR_BG_DARK,
    COLOR_BG_CARD,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_SKY,
    COLOR_ACCENT_PURPLE,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    aplicar_icono,
    centrar_ventana,
)
from KernossAI.core.i18n import t
from KernossAI.core.auth import (
    tutoria_listar_profesores,
    tutoria_enviar_solicitud,
    tutoria_obtener_estado_alumno,
    tutoria_profesor_obtener_solicitudes_y_alumnos,
    tutoria_profesor_responder_solicitud,
    tutoria_enviar_mensaje,
    tutoria_obtener_mensajes_chat,
    tutoria_desvincular,
)


class VentanaTutoriaAlumnoProfesor(ctk.CTkToplevel):
    """Sistema integral de tutoría académica entre Alumnos y Docentes con cifrado E2EE."""
    def __init__(self, parent, sesion):
        super().__init__(parent)
        self.parent = parent
        self.sesion = sesion
        self.rol = sesion.get("rol", "Alumno")
        self.email = sesion.get("email", "").strip().lower()
        self.nombre = sesion.get("nombre", self.email)
        
        titulo = t("tutoria_modal_titulo_alumno") if self.rol == "Alumno" else t("tutoria_modal_titulo_profesor")
        self.title(titulo)
        self.geometry("920x720")
        self.minsize(780, 560)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        aplicar_icono(self)
        centrar_ventana(self, 920, 720)

        self._polling_activo = True
        self._profesores = []
        self._estado_vinculacion = None
        self._solicitudes_pendientes = []
        self._alumnos_vinculados = []
        self._alumno_activo_chat = None
        self._mensajes_chat = []

        self._build_ui()
        self._iniciar_carga()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, height=75, corner_radius=0)
        header.pack(fill="x")

        frame_h_info = ctk.CTkFrame(header, fg_color="transparent")
        frame_h_info.pack(side="left", padx=20, pady=12)

        tit_header = t("tutoria_modal_titulo_alumno") if self.rol == "Alumno" else t("tutoria_modal_titulo_profesor")
        ctk.CTkLabel(frame_h_info, text=tit_header, font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")

        ctk.CTkLabel(frame_h_info, text="🔒 E2EE • End-to-End Encryption",
                     font=("Segoe UI", 10, "bold"), text_color=COLOR_ACCENT_CYAN).pack(anchor="w")

        btn_cerrar = ctk.CTkButton(header, text="✕", width=36, height=36, fg_color=COLOR_BG_CARD,
                                   hover_color=COLOR_DANGER, font=("Segoe UI", 14, "bold"), command=self._cerrar)
        btn_cerrar.pack(side="right", padx=16)

        self.contenedor_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_principal.pack(fill="both", expand=True, padx=15, pady=12)

        if self.rol == "Alumno":
            self._build_ui_alumno()
        else:
            self._build_ui_profesor()

    def _build_ui_alumno(self):
        self.frame_alumno_dinamico = ctk.CTkFrame(self.contenedor_principal, fg_color="transparent")
        self.frame_alumno_dinamico.pack(fill="both", expand=True)

    def _renderizar_alumno_estado(self):
        for w in self.frame_alumno_dinamico.winfo_children():
            w.destroy()

        vinc = self._estado_vinculacion
        estado = vinc.get("estado") if vinc else None

        if not vinc or estado == "rechazada":
            self._render_alumno_selector_profesores()
        elif estado == "pendiente":
            self._render_alumno_solicitud_pendiente(vinc)
        elif estado == "aceptada":
            self._render_alumno_chat_tutor(vinc)

    def _render_alumno_selector_profesores(self):
        card_info = ctk.CTkFrame(self.frame_alumno_dinamico, fg_color=COLOR_BG_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        card_info.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(card_info, text=t("tutoria_tab_profesores"), font=("Segoe UI", 13, "bold"), text_color=COLOR_ACCENT_SKY).pack(anchor="w", padx=14, pady=(10, 2))

        frame_busq = ctk.CTkFrame(self.frame_alumno_dinamico, fg_color="transparent")
        frame_busq.pack(fill="x", pady=(0, 8))
        self.entry_busq_profe = ctk.CTkEntry(
            frame_busq, height=36, font=("Segoe UI", 11),
            placeholder_text="🔍 Buscar profesor por nombre o email...",
            fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER
        )
        self.entry_busq_profe.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_busq_profe.bind("<KeyRelease>", lambda e: self._filtrar_profesores_ui())

        ctk.CTkButton(
            frame_busq, text="🔄", width=45, height=36,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_BG_SURFACE,
            hover_color=COLOR_ACCENT_HOVER, command=self._cargar_profesores_alumno
        ).pack(side="right")

        self.scroll_profes = ctk.CTkScrollableFrame(self.frame_alumno_dinamico, fg_color=COLOR_BG_SURFACE, corner_radius=10)
        self.scroll_profes.pack(fill="both", expand=True)
        self._filtrar_profesores_ui()

    def _filtrar_profesores_ui(self):
        for w in self.scroll_profes.winfo_children():
            w.destroy()

        filtro = self.entry_busq_profe.get().strip().lower() if hasattr(self, "entry_busq_profe") else ""
        profes_filtrados = [
            p for p in self._profesores
            if filtro in p.get("nombre", "").lower() or filtro in p.get("email", "").lower()
        ]

        if not profes_filtrados:
            ctk.CTkLabel(self.scroll_profes, text=t("tutoria_sin_profes"),
                         font=("Segoe UI", 12), text_color=COLOR_TEXT_MUTED).pack(pady=40)
            return

        for p in profes_filtrados:
            p_email = p.get("email", "").strip()
            p_nombre = p.get("nombre", p_email)

            card = ctk.CTkFrame(self.scroll_profes, fg_color=COLOR_BG_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
            card.pack(fill="x", padx=6, pady=4)

            f_left = ctk.CTkFrame(card, fg_color="transparent")
            f_left.pack(side="left", fill="x", expand=True, padx=14, pady=10)

            ctk.CTkLabel(f_left, text=f"👨‍🏫 {p_nombre}", font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(f_left, text=f"✉️ {p_email}", font=("Segoe UI", 10), text_color=COLOR_ACCENT_CYAN).pack(anchor="w", pady=(2, 0))

            btn_solicitar = ctk.CTkButton(
                card, text=t("tutoria_btn_solicitar"), height=32, width=170,
                font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_PRIMARY,
                hover_color=COLOR_ACCENT_HOVER,
                command=lambda em=p_email, nm=p_nombre: self._modal_enviar_solicitud(em, nm)
            )
            btn_solicitar.pack(side="right", padx=14, pady=10)

    def _modal_enviar_solicitud(self, profesor_email: str, profesor_nombre: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("tutoria_btn_solicitar"))
        dialog.geometry("480x280")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLOR_BG_DARK)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"📨 {profesor_nombre}", font=("Segoe UI", 14, "bold"), text_color=COLOR_ACCENT_SKY).pack(pady=(16, 4))
        ctk.CTkLabel(dialog, text=f"Docente: {profesor_email}", font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 10))

        entry_msg = ctk.CTkEntry(dialog, height=36, font=("Segoe UI", 11), fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        entry_msg.pack(fill="x", padx=25, pady=(0, 15))
        entry_msg.insert(0, "Hola, me gustaría vincularme como alumno para tutoría académica.")

        def _enviar():
            msg_texto = entry_msg.get().strip()
            dialog.destroy()
            def _thread():
                ok, res = tutoria_enviar_solicitud(profesor_email, profesor_nombre, msg_texto)
                if ok:
                    self.after(0, lambda: messagebox.showinfo("Tutoría", res))
                    self._iniciar_carga()
                else:
                    self.after(0, lambda: messagebox.showerror("Error", res))
            threading.Thread(target=_thread, daemon=True).start()

        frame_btns = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_btns.pack(fill="x", padx=25, pady=(0, 15))
        ctk.CTkButton(frame_btns, text=t("tutoria_btn_solicitar"), font=("Segoe UI", 12, "bold"), fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER, height=36, command=_enviar).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(frame_btns, text=t("ajustes_btn_cancelar"), font=("Segoe UI", 11), fg_color=COLOR_BG_SURFACE, hover_color=COLOR_BORDER, height=36, width=80, command=dialog.destroy).pack(side="right")

    def _render_alumno_solicitud_pendiente(self, vinc: dict):
        p_nombre = vinc.get("profesor_nombre", "Profesor")
        p_email = vinc.get("profesor_email", "")
        fecha = vinc.get("timestamp", "")[:16].replace("T", " ")

        card = ctk.CTkFrame(self.frame_alumno_dinamico, fg_color=COLOR_BG_CARD, corner_radius=12, border_width=1, border_color="#eab308")
        card.pack(fill="x", pady=20, padx=20)

        ctk.CTkLabel(card, text="⏳ Solicitud Pendiente", font=("Segoe UI", 16, "bold"), text_color="#fde047").pack(pady=(18, 6))
        ctk.CTkLabel(card, text=t("tutoria_solicitud_pendiente", nombre=p_nombre, email=p_email), font=("Segoe UI", 12), text_color=COLOR_TEXT_MAIN).pack(pady=(0, 4))
        ctk.CTkLabel(card, text=f"🕒 {fecha}", font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED, justify="center").pack(pady=(0, 14))

        frame_btns = ctk.CTkFrame(card, fg_color="transparent")
        frame_btns.pack(pady=(0, 18))

        ctk.CTkButton(
            frame_btns, text="🔄 Actualizar", font=("Segoe UI", 11, "bold"),
            fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER, height=34,
            command=self._iniciar_carga
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            frame_btns, text=t("tutoria_btn_desvincular"), font=("Segoe UI", 11),
            fg_color="#7f1d1d", hover_color="#991b1b", border_width=1, border_color=COLOR_DANGER, height=34,
            command=lambda: self._desvincular_confirm(p_email)
        ).pack(side="left", padx=6)

    def _render_alumno_chat_tutor(self, vinc: dict):
        p_nombre = vinc.get("profesor_nombre", "Profesor")
        p_email = vinc.get("profesor_email", "")

        hdr_chat = ctk.CTkFrame(self.frame_alumno_dinamico, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        hdr_chat.pack(fill="x", pady=(0, 8))

        f_tit = ctk.CTkFrame(hdr_chat, fg_color="transparent")
        f_tit.pack(side="left", padx=14, pady=10)
        ctk.CTkLabel(f_tit, text=f"👨‍🏫 {p_nombre}", font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(f_tit, text=f"✉️ {p_email}   •   🟢 Canal E2EE Activo", font=("Segoe UI", 10), text_color=COLOR_SUCCESS).pack(anchor="w")

        ctk.CTkButton(
            hdr_chat, text=t("tutoria_btn_desvincular"), font=("Segoe UI", 10, "bold"),
            fg_color="#7f1d1d", hover_color="#991b1b", height=28, width=100,
            command=lambda: self._desvincular_confirm(p_email)
        ).pack(side="right", padx=14)

        self.scroll_chat_alumno = ctk.CTkScrollableFrame(self.frame_alumno_dinamico, fg_color=COLOR_BG_DARK)
        self.scroll_chat_alumno.pack(fill="both", expand=True, pady=(0, 8))

        f_input = ctk.CTkFrame(self.frame_alumno_dinamico, fg_color=COLOR_BG_SURFACE, corner_radius=10)
        f_input.pack(fill="x")

        self.entry_msg_alumno = ctk.CTkEntry(
            f_input, height=40, font=("Segoe UI", 11),
            placeholder_text="Escribe tu consulta académica a tu profesor...",
            fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER
        )
        self.entry_msg_alumno.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.entry_msg_alumno.bind("<Return>", lambda e: self._enviar_msg_alumno(p_email))

        self.btn_enviar_alumno = ctk.CTkButton(
            f_input, text="📤", width=60, height=40,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_PRIMARY,
            hover_color=COLOR_ACCENT_HOVER, command=lambda: self._enviar_msg_alumno(p_email)
        )
        self.btn_enviar_alumno.pack(side="right", padx=(0, 10), pady=10)

        self._cargar_mensajes_alumno(p_email)

    def _enviar_msg_alumno(self, p_email: str):
        texto = self.entry_msg_alumno.get().strip()
        if not texto:
            return
        self.entry_msg_alumno.delete(0, "end")
        self.btn_enviar_alumno.configure(state="disabled")

        def _thread():
            ok, _ = tutoria_enviar_mensaje(p_email, texto)
            if ok:
                self._cargar_mensajes_alumno(p_email)
            self.after(0, lambda: self.btn_enviar_alumno.configure(state="normal"))

        threading.Thread(target=_thread, daemon=True).start()

    def _cargar_mensajes_alumno(self, p_email: str):
        def _thread():
            ok, msgs = tutoria_obtener_mensajes_chat(p_email)
            if ok:
                self._mensajes_chat = msgs
                self.after(0, self._render_mensajes_alumno_ui)

        threading.Thread(target=_thread, daemon=True).start()

    def _render_mensajes_alumno_ui(self):
        if not hasattr(self, "scroll_chat_alumno"):
            return
        for w in self.scroll_chat_alumno.winfo_children():
            w.destroy()

        for m in self._mensajes_chat:
            es_mio = m.get("es_mio", False)
            emisor = "Tú" if es_mio else f"👨‍🏫 {m.get('emisor_nombre', 'Profesor')}"
            hora = m.get("timestamp", "")[11:16] if m.get("timestamp") else ""
            texto = m.get("texto", "")

            frame_b = ctk.CTkFrame(
                self.scroll_chat_alumno,
                fg_color=COLOR_ACCENT_PRIMARY if es_mio else COLOR_BG_CARD,
                corner_radius=10,
                border_width=1,
                border_color=COLOR_ACCENT_HOVER if es_mio else COLOR_BORDER
            )
            frame_b.pack(anchor="e" if es_mio else "w", padx=10, pady=4)

            hdr = f"{emisor} • 🕒 {hora}"
            ctk.CTkLabel(frame_b, text=hdr, font=("Segoe UI", 9, "bold"),
                         text_color="#bfdbfe" if es_mio else COLOR_ACCENT_CYAN).pack(anchor="w", padx=10, pady=(6, 1))

            ctk.CTkLabel(frame_b, text=texto, font=("Segoe UI", 11),
                         text_color="#ffffff", wraplength=440, justify="left").pack(anchor="w", padx=10, pady=(0, 8))

        self.scroll_chat_alumno._parent_canvas.yview_moveto(1.0)

    # ─────────────────────────────────────────────────────────
    #  VISTA DEL PROFESOR
    # ─────────────────────────────────────────────────────────
    def _build_ui_profesor(self):
        self.tabview_profesor = ctk.CTkTabview(self.contenedor_principal, fg_color=COLOR_BG_DARK)
        self.tabview_profesor.pack(fill="both", expand=True)

        self.tab_solicitudes = self.tabview_profesor.add("solicitudes")
        self.tab_alumnos = self.tabview_profesor.add("alumnos")

        self.lbl_num_solicitudes = self.tabview_profesor._segmented_button._buttons_dict["solicitudes"]
        self.lbl_num_solicitudes.configure(text=f"{t('tutoria_tab_solicitudes')} (0)")
        self.tabview_profesor._segmented_button._buttons_dict["alumnos"].configure(text=t("tutoria_tab_alumnos"))

        self._build_tab_profesor_solicitudes()
        self._build_tab_profesor_alumnos()

    def _build_tab_profesor_solicitudes(self):
        self.scroll_solicitudes = ctk.CTkScrollableFrame(self.tab_solicitudes, fg_color=COLOR_BG_SURFACE, corner_radius=10)
        self.scroll_solicitudes.pack(fill="both", expand=True, padx=4, pady=4)

    def _render_profesor_solicitudes(self):
        for w in self.scroll_solicitudes.winfo_children():
            w.destroy()

        n = len(self._solicitudes_pendientes)
        self.lbl_num_solicitudes.configure(text=f"{t('tutoria_tab_solicitudes')} ({n})")

        if not self._solicitudes_pendientes:
            ctk.CTkLabel(self.scroll_solicitudes, text="✨ No tienes solicitudes pendientes de alumnos.",
                         font=("Segoe UI", 12), text_color=COLOR_TEXT_MUTED).pack(pady=40)
            return

        for s in self._solicitudes_pendientes:
            a_email = s.get("alumno_email", "")
            a_nombre = s.get("alumno_nombre", a_email)
            msg = s.get("mensaje", "")
            fecha = s.get("timestamp", "")[:16].replace("T", " ")

            card = ctk.CTkFrame(self.scroll_solicitudes, fg_color=COLOR_BG_CARD, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
            card.pack(fill="x", padx=4, pady=4)

            f_info = ctk.CTkFrame(card, fg_color="transparent")
            f_info.pack(side="left", fill="x", expand=True, padx=14, pady=10)

            ctk.CTkLabel(f_info, text=f"🎓 {a_nombre}", font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(f_info, text=f"✉️ {a_email}   •   🕒 {fecha}", font=("Segoe UI", 10), text_color=COLOR_ACCENT_CYAN).pack(anchor="w", pady=(1, 3))
            if msg:
                ctk.CTkLabel(f_info, text=f"💬 \"{msg}\"", font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED, wraplength=420, justify="left").pack(anchor="w")

            f_actions = ctk.CTkFrame(card, fg_color="transparent")
            f_actions.pack(side="right", padx=12, pady=10)

            ctk.CTkButton(
                f_actions, text=t("tutoria_btn_aceptar"), width=125, height=32,
                font=("Segoe UI", 11, "bold"), fg_color=COLOR_SUCCESS, hover_color="#15803d",
                command=lambda em=a_email: self._responder_solicitud_profesor(em, True)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                f_actions, text=t("tutoria_btn_rechazar"), width=95, height=32,
                font=("Segoe UI", 11), fg_color="#7f1d1d", hover_color="#991b1b", border_width=1, border_color=COLOR_DANGER,
                command=lambda em=a_email: self._responder_solicitud_profesor(em, False)
            ).pack(side="left", padx=4)

    def _responder_solicitud_profesor(self, alumno_email: str, aceptar: bool):
        def _thread():
            ok, res = tutoria_profesor_responder_solicitud(alumno_email, aceptar)
            if ok:
                self.after(0, lambda: messagebox.showinfo("Tutoría", res))
                self._iniciar_carga()
            else:
                self.after(0, lambda: messagebox.showerror("Error", res))

        threading.Thread(target=_thread, daemon=True).start()

    def _build_tab_profesor_alumnos(self):
        split = ctk.CTkFrame(self.tab_alumnos, fg_color="transparent")
        split.pack(fill="both", expand=True)
        split.grid_columnconfigure(0, weight=4)
        split.grid_columnconfigure(1, weight=6)
        split.grid_rowconfigure(0, weight=1)

        col_izq = ctk.CTkFrame(split, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)

        ctk.CTkLabel(col_izq, text=t("tutoria_tab_alumnos"), font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=14, pady=(10, 6))

        self.scroll_alumnos_profesor = ctk.CTkScrollableFrame(col_izq, fg_color="transparent")
        self.scroll_alumnos_profesor.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        self.col_der_profesor = ctk.CTkFrame(split, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.col_der_profesor.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)
        self.col_der_profesor.grid_rowconfigure(1, weight=1)
        self.col_der_profesor.grid_columnconfigure(0, weight=1)

        self.hdr_chat_profe = ctk.CTkFrame(self.col_der_profesor, fg_color=COLOR_BG_CARD, height=50, corner_radius=8)
        self.hdr_chat_profe.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        self.lbl_chat_alumno_info = ctk.CTkLabel(
            self.hdr_chat_profe, text="Selecciona un alumno vinculado para chatear",
            font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MUTED
        )
        self.lbl_chat_alumno_info.pack(side="left", padx=12, pady=10)

        self.btn_desvincular_alumno_profe = ctk.CTkButton(
            self.hdr_chat_profe, text=t("tutoria_btn_desvincular"), width=100, height=28,
            font=("Segoe UI", 10, "bold"), fg_color="#7f1d1d", hover_color="#991b1b",
            command=self._desvincular_alumno_desde_profe
        )

        self.scroll_mensajes_profe = ctk.CTkScrollableFrame(self.col_der_profesor, fg_color=COLOR_BG_DARK)
        self.scroll_mensajes_profe.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)

        barra_resp = ctk.CTkFrame(self.col_der_profesor, fg_color="transparent")
        barra_resp.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 10))

        self.entry_resp_profe = ctk.CTkEntry(
            barra_resp, font=("Segoe UI", 11), height=38,
            placeholder_text="Escribe tu respuesta académica al alumno...",
            fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER
        )
        self.entry_resp_profe.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_resp_profe.bind("<Return>", lambda e: self._enviar_msg_profesor())

        self.btn_enviar_resp_profe = ctk.CTkButton(
            barra_resp, text="Responder 📤", width=115, height=38,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_PURPLE,
            hover_color="#7e22ce", command=self._enviar_msg_profesor,
            state="disabled"
        )
        self.btn_enviar_resp_profe.pack(side="right")

    def _render_profesor_alumnos(self):
        for w in self.scroll_alumnos_profesor.winfo_children():
            w.destroy()

        if not self._alumnos_vinculados:
            ctk.CTkLabel(self.scroll_alumnos_profesor, text="No tienes alumnos vinculados aún.\nCuando aceptes solicitudes aparecerán aquí.",
                         font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED, justify="center").pack(pady=30)
            return

        for a in self._alumnos_vinculados:
            a_email = a.get("alumno_email", "")
            a_nombre = a.get("alumno_nombre", a_email)

            card = ctk.CTkFrame(self.scroll_alumnos_profesor, fg_color=COLOR_BG_CARD, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
            card.pack(fill="x", padx=2, pady=3)

            f_txt = ctk.CTkFrame(card, fg_color="transparent")
            f_txt.pack(fill="x", padx=8, pady=6)

            ctk.CTkLabel(f_txt, text=f"🎓 {a_nombre}", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(f_txt, text=a_email, font=("Segoe UI", 9), text_color=COLOR_ACCENT_CYAN).pack(anchor="w")

            ctk.CTkButton(
                card, text="💬 Abrir Tutoría", height=26, font=("Segoe UI", 10, "bold"),
                fg_color=COLOR_ACCENT_PURPLE, hover_color="#7e22ce",
                command=lambda em=a_email, nm=a_nombre: self._seleccionar_alumno_chat_profe(em, nm)
            ).pack(fill="x", padx=8, pady=(0, 6))

    def _seleccionar_alumno_chat_profe(self, a_email: str, a_nombre: str):
        self._alumno_activo_chat = {"email": a_email, "nombre": a_nombre}
        self.lbl_chat_alumno_info.configure(text=f"🎓 Alumno: {a_nombre} ({a_email})", text_color=COLOR_TEXT_MAIN)
        self.btn_desvincular_alumno_profe.pack(side="right", padx=10, pady=8)
        self.btn_enviar_resp_profe.configure(state="normal")
        self.entry_resp_profe.focus_set()
        self._cargar_mensajes_profesor_ui()

    def _cargar_mensajes_profesor_ui(self):
        if not self._alumno_activo_chat:
            return
        a_email = self._alumno_activo_chat["email"]

        def _thread():
            ok, msgs = tutoria_obtener_mensajes_chat(a_email)
            if ok:
                def _render():
                    for w in self.scroll_mensajes_profe.winfo_children():
                        w.destroy()

                    for m in msgs:
                        es_mio = m.get("es_mio", False)
                        emisor = "Tú (Profesor)" if es_mio else f"🎓 {m.get('emisor_nombre', 'Alumno')}"
                        hora = m.get("timestamp", "")[11:16] if m.get("timestamp") else ""
                        texto = m.get("texto", "")

                        frame_b = ctk.CTkFrame(
                            self.scroll_mensajes_profe,
                            fg_color=COLOR_ACCENT_PURPLE if es_mio else COLOR_BG_CARD,
                            corner_radius=10,
                            border_width=1,
                            border_color="#a855f7" if es_mio else COLOR_BORDER
                        )
                        frame_b.pack(anchor="e" if es_mio else "w", padx=8, pady=4)

                        hdr = f"{emisor} • 🕒 {hora}"
                        ctk.CTkLabel(frame_b, text=hdr, font=("Segoe UI", 9, "bold"),
                                     text_color="#e9d5ff" if es_mio else COLOR_ACCENT_CYAN).pack(anchor="w", padx=10, pady=(6, 1))

                        ctk.CTkLabel(frame_b, text=texto, font=("Segoe UI", 11),
                                     text_color="#ffffff", wraplength=380, justify="left").pack(anchor="w", padx=10, pady=(0, 8))

                    self.scroll_mensajes_profe._parent_canvas.yview_moveto(1.0)
                self.after(0, _render)

        threading.Thread(target=_thread, daemon=True).start()

    def _enviar_msg_profesor(self):
        if not self._alumno_activo_chat:
            return
        a_email = self._alumno_activo_chat["email"]
        texto = self.entry_resp_profe.get().strip()
        if not texto:
            return

        self.entry_resp_profe.delete(0, "end")
        self.btn_enviar_resp_profe.configure(state="disabled")

        def _thread():
            ok, _ = tutoria_enviar_mensaje(a_email, texto)
            if ok:
                self._cargar_mensajes_profesor_ui()
            self.after(0, lambda: self.btn_enviar_resp_profe.configure(state="normal"))

        threading.Thread(target=_thread, daemon=True).start()

    def _desvincular_alumno_desde_profe(self):
        if not self._alumno_activo_chat:
            return
        a_email = self._alumno_activo_chat["email"]
        self._desvincular_confirm(a_email)

    def _desvincular_confirm(self, otro_email: str):
        confirm = messagebox.askyesno(
            "⚠️ Finalizar Vinculación",
            f"¿Estás seguro de que deseas finalizar la vinculación con '{otro_email}'?\n\n"
            "• Se cerrará el canal de tutoría actual.\n"
            "• El alumno podrá solicitar unirse a otro profesor.\n\n"
            "¿Deseas continuar?"
        )
        if not confirm:
            return

        def _thread():
            ok, msg = tutoria_desvincular(otro_email)
            if ok:
                self.after(0, lambda: messagebox.showinfo("Tutoría", msg))
                self.after(0, self._iniciar_carga)
            else:
                self.after(0, lambda: messagebox.showerror("Error", msg))

        threading.Thread(target=_thread, daemon=True).start()

    def _iniciar_carga(self):
        if self.rol == "Alumno":
            self._cargar_datos_alumno()
        else:
            self._cargar_datos_profesor()

    def _cargar_datos_alumno(self):
        def _thread():
            ok_v, vinc = tutoria_obtener_estado_alumno()
            self._estado_vinculacion = vinc if ok_v else None

            if not self._estado_vinculacion or self._estado_vinculacion.get("estado") == "rechazada":
                ok_p, profes = tutoria_listar_profesores()
                self._profesores = profes if ok_p else []

            self.after(0, self._renderizar_alumno_estado)

        threading.Thread(target=_thread, daemon=True).start()

    def _cargar_profesores_alumno(self):
        def _thread():
            ok_p, profes = tutoria_listar_profesores()
            if ok_p:
                self._profesores = profes
                self.after(0, self._filtrar_profesores_ui)

        threading.Thread(target=_thread, daemon=True).start()

    def _cargar_datos_profesor(self):
        def _thread():
            ok, pend, acept = tutoria_profesor_obtener_solicitudes_y_alumnos()
            if ok:
                self._solicitudes_pendientes = pend
                self._alumnos_vinculados = acept
                self.after(0, lambda: (
                    self._render_profesor_solicitudes(),
                    self._render_profesor_alumnos()
                ))

        threading.Thread(target=_thread, daemon=True).start()

    def _cerrar(self):
        self._polling_activo = False
        self.destroy()
