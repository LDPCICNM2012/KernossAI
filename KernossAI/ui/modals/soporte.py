"""
KernossAI - Módulo de Soporte Oficial y Bandeja de Tickets E2EE
Canal de atención al usuario y bandeja de soporte con cifrado de extremo a extremo.
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
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    aplicar_icono,
    centrar_ventana,
)
from KernossAI.core.auth import (
    enviar_mensaje_soporte,
    obtener_mensajes_soporte,
    admin_obtener_tickets_soporte,
    admin_responder_ticket_soporte,
    admin_borrar_ticket_soporte,
)
from KernossAI.core.i18n import t, obtener_idioma_activo


class VentanaSoporteE2EE(ctk.CTkToplevel):
    """Canal oficial de atención al usuario y soporte técnico con cifrado de extremo a extremo (E2EE)."""
    def __init__(self, parent, sesion):
        super().__init__(parent)
        self.parent = parent
        self.sesion = sesion
        self.email = sesion.get("email", "")
        self.nombre = sesion.get("nombre", "Usuario")
        self.title(t("sop_titulo_ventana"))
        self.geometry("780x680")
        self.minsize(640, 520)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        aplicar_icono(self)
        centrar_ventana(self, 780, 680)

        self._mensajes = []
        self._polling_activo = True
        self._build_ui()
        self._iniciar_polling()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, height=75, corner_radius=0)
        header.pack(fill="x")
        
        frame_h_info = ctk.CTkFrame(header, fg_color="transparent")
        frame_h_info.pack(side="left", padx=20, pady=12)
        
        ctk.CTkLabel(frame_h_info, text="🛡️ Support Official KernossAI (kernossai@support.com)",
                     font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
        
        badge_sec = ctk.CTkLabel(frame_h_info, text=t("sop_subtitulo"),
                                 font=("Segoe UI", 10, "bold"), text_color=COLOR_SUCCESS)
        badge_sec.pack(anchor="w")

        btn_cerrar = ctk.CTkButton(header, text="✕", width=36, height=36, fg_color=COLOR_BG_CARD,
                                   hover_color=COLOR_DANGER, font=("Segoe UI", 14, "bold"), command=self._cerrar)
        btn_cerrar.pack(side="right", padx=16)

        self.scroll_chat = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_DARK)
        self.scroll_chat.pack(fill="both", expand=True, padx=20, pady=(12, 10))

        barra_input = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, corner_radius=0)
        barra_input.pack(fill="x", side="bottom")

        aviso_beta = ctk.CTkFrame(barra_input, fg_color="transparent")
        aviso_beta.pack(fill="x", padx=18, pady=(8, 2))

        ctk.CTkLabel(
            aviso_beta,
            text=t("sop_aviso_beta"),
            font=("Segoe UI", 9, "bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(side="left")

        fila_motivo = ctk.CTkFrame(barra_input, fg_color="transparent")
        fila_motivo.pack(fill="x", padx=18, pady=(2, 2))

        ctk.CTkLabel(fila_motivo, text=t("sop_lbl_motivo"), font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=(0, 8))

        motivos_map = {
            "es": ["Duda Académica / Tareas", "Problema con la IA", "Error o Bug del Programa", "Problema con mi Cuenta", "Sugerencia / Idea", "Consulta General"],
            "en": ["Academic / Homework Doubt", "Issue with AI", "Software Bug / Error", "Account Issue", "Suggestion / Feature Idea", "General Inquiry"],
            "de": ["Lernfrage / Hausaufgaben", "KI-Problem", "Programmfehler / Bug", "Kontoproblem", "Vorschlag / Idee", "Allgemeine Anfrage"],
            "fr": ["Question Académique / Devoirs", "Problème avec l'IA", "Bug / Erreur du Logiciel", "Problème de Compte", "Suggestion / Idée", "Demande Générale"]
        }
        lista_motivos = motivos_map.get(obtener_idioma_activo(), motivos_map["es"])

        self.combo_motivo = ctk.CTkComboBox(
            fila_motivo, values=lista_motivos, font=("Segoe UI", 10),
            fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, height=26, width=240
        )
        self.combo_motivo.set(lista_motivos[0])
        self.combo_motivo.pack(side="left")

        fila_campo = ctk.CTkFrame(barra_input, fg_color="transparent")
        fila_campo.pack(fill="x", padx=18, pady=(4, 12))

        self.entry_msg = ctk.CTkEntry(
            fila_campo, placeholder_text=t("sop_placeholder_input"),
            font=("Segoe UI", 12), fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, height=42
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda e: self._enviar_mensaje())

        self.btn_enviar = ctk.CTkButton(
            fila_campo, text=t("sop_btn_enviar"), font=("Segoe UI", 12, "bold"),
            fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
            width=110, height=42, command=self._enviar_mensaje
        )
        self.btn_enviar.pack(side="right")

    def _iniciar_polling(self):
        def _loop():
            self._cargar_mensajes()
            if self._polling_activo:
                self.after(4000, self._iniciar_polling)
        threading.Thread(target=_loop, daemon=True).start()

    def _cargar_mensajes(self):
        ok, msgs = obtener_mensajes_soporte()
        if ok and msgs != self._mensajes:
            self._mensajes = msgs
            self.after(0, self._renderizar_chat)

    def _renderizar_chat(self):
        for w in self.scroll_chat.winfo_children():
            w.destroy()

        if not self._mensajes:
            f_bienv = ctk.CTkFrame(self.scroll_chat, fg_color=COLOR_BG_CARD, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
            f_bienv.pack(fill="x", padx=15, pady=20)

            ctk.CTkLabel(f_bienv, text="🛡️ Soporte Oficial KernossAI", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(padx=20, pady=(16, 4))
            ctk.CTkLabel(f_bienv, text=t("sop_aviso_intro"), font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED, justify="left", wraplength=520).pack(padx=20, pady=(0, 16))
            return

        for m in self._mensajes:
            es_soporte = m.get("es_soporte", False)
            emisor = "🛡️ Soporte Oficial" if es_soporte else f"👤 {self.nombre}"
            hora = m.get("timestamp", "")[:19].replace("T", " ") if m.get("timestamp") else ""
            texto = m.get("texto", "")

            frame_burbuja = ctk.CTkFrame(
                self.scroll_chat,
                fg_color="#065f46" if es_soporte else COLOR_BG_SURFACE,
                corner_radius=12,
                border_width=1,
                border_color="#10b981" if es_soporte else COLOR_BORDER
            )
            frame_burbuja.pack(anchor="w" if es_soporte else "e", padx=10, pady=5, fill="none")

            hdr = f"{emisor} • 🕒 {hora}"
            ctk.CTkLabel(frame_burbuja, text=hdr, font=("Segoe UI", 9, "bold"),
                         text_color="#6ee7b7" if es_soporte else COLOR_ACCENT_CYAN).pack(anchor="w", padx=12, pady=(8, 2))

            ctk.CTkLabel(frame_burbuja, text=texto, font=("Segoe UI", 11),
                         text_color="#ffffff" if es_soporte else COLOR_TEXT_MAIN,
                         wraplength=480, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        self.scroll_chat._parent_canvas.yview_moveto(1.0)

    def _enviar_mensaje(self):
        texto = self.entry_msg.get().strip()
        if not texto:
            return
        motivo = self.combo_motivo.get() if hasattr(self, "combo_motivo") else "Consulta General"
        self.entry_msg.delete(0, "end")
        self.btn_enviar.configure(state="disabled")

        def _thread():
            ok, res = enviar_mensaje_soporte(texto, motivo=motivo)
            if ok:
                self._cargar_mensajes()
            else:
                self.after(0, lambda: messagebox.showerror("Error Soporte", res))
            self.after(0, lambda: self.btn_enviar.configure(state="normal"))

        threading.Thread(target=_thread, daemon=True).start()

    def _cerrar(self):
        self._polling_activo = False
        self.destroy()


class VentanaBandejaSoporte(ctk.CTkToplevel):
    """Bandeja de Entrada exclusiva para atención de tickets de soporte oficial con cifrado E2EE."""
    def __init__(self, parent, sesion):
        super().__init__(parent)
        self.parent = parent
        self.sesion = sesion
        self.title("📬 Bandeja de Entrada — Soporte Oficial KernossAI")
        self.geometry("980x720")
        self.minsize(800, 580)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        aplicar_icono(self)
        centrar_ventana(self, 980, 720)

        self._ticket_activo_email = None
        self._build_ui()
        self._cargar_tickets_soporte()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, height=65, corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(header, text="📬 Bandeja de Entrada — Soporte Oficial (kernossai@support.com)",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=20, pady=16)

        btn_refrescar = ctk.CTkButton(header, text="🔄 Actualizar Tickets", width=150, height=32,
                                      font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_PRIMARY,
                                      hover_color=COLOR_ACCENT_HOVER, command=self._cargar_tickets_soporte)
        btn_refrescar.pack(side="right", padx=(10, 20))

        btn_cerrar = ctk.CTkButton(header, text="✕", width=36, height=36, fg_color=COLOR_BG_CARD,
                                   hover_color=COLOR_DANGER, font=("Segoe UI", 14, "bold"), command=self.destroy)
        btn_cerrar.pack(side="right", padx=6)

        self.frame_inbox_split = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inbox_split.pack(fill="both", expand=True, padx=15, pady=12)
        self.frame_inbox_split.grid_columnconfigure(0, weight=4)
        self.frame_inbox_split.grid_columnconfigure(1, weight=6)
        self.frame_inbox_split.grid_rowconfigure(0, weight=1)

        col_izq = ctk.CTkFrame(self.frame_inbox_split, fg_color=COLOR_BG_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)
        
        ctk.CTkLabel(col_izq, text="📬 Mensajes Recibidos de Alumnos", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=14, pady=(12, 6))

        self.scroll_tickets = ctk.CTkScrollableFrame(col_izq, fg_color="transparent")
        self.scroll_tickets.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        self.col_der = ctk.CTkFrame(self.frame_inbox_split, fg_color=COLOR_BG_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        self.col_der.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)
        self.col_der.grid_rowconfigure(1, weight=1)
        self.col_der.grid_columnconfigure(0, weight=1)

        self.hdr_chat_soporte = ctk.CTkFrame(self.col_der, fg_color=COLOR_BG_CARD, height=55, corner_radius=8)
        self.hdr_chat_soporte.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        
        self.lbl_chat_usr_info = ctk.CTkLabel(self.hdr_chat_soporte, text="Selecciona un ticket a la izquierda para responder",
                                              font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MUTED)
        self.lbl_chat_usr_info.pack(side="left", padx=14, pady=12)

        self.btn_borrar_chat = ctk.CTkButton(
            self.hdr_chat_soporte, text="🗑️ Vaciar Chat", width=105, height=30,
            font=("Segoe UI", 10, "bold"), fg_color="#7f1d1d", hover_color="#991b1b",
            border_width=1, border_color=COLOR_DANGER, command=self._borrar_conversacion_ticket
        )

        self.scroll_mensajes_soporte = ctk.CTkScrollableFrame(self.col_der, fg_color=COLOR_BG_DARK)
        self.scroll_mensajes_soporte.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)

        barra_resp = ctk.CTkFrame(self.col_der, fg_color="transparent")
        barra_resp.grid(row=2, column=0, sticky="ew", padx=10, pady=(6, 12))

        self.entry_resp_soporte = ctk.CTkEntry(
            barra_resp, font=("Segoe UI", 11), height=38,
            placeholder_text="Escribe la respuesta oficial al alumno...",
            fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER
        )
        self.entry_resp_soporte.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_resp_soporte.bind("<Return>", lambda e: self._enviar_respuesta_soporte())

        self.btn_enviar_resp = ctk.CTkButton(
            barra_resp, text="Responder 📤", width=115, height=38,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_SUCCESS,
            hover_color="#15803d", command=self._enviar_respuesta_soporte,
            state="disabled"
        )
        self.btn_enviar_resp.pack(side="right")

    def _cargar_tickets_soporte(self):
        for w in self.scroll_tickets.winfo_children():
            w.destroy()

        def _thread():
            ok, tickets = admin_obtener_tickets_soporte()
            if not ok:
                return

            def _render():
                if not hasattr(self, "scroll_tickets") or not self.winfo_exists():
                    return
                for w in self.scroll_tickets.winfo_children():
                    w.destroy()
                if not tickets:
                    ctk.CTkLabel(self.scroll_tickets, text="No hay tickets de soporte aún.",
                                 font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED).pack(pady=30)
                    return

                for t_item in tickets:
                    u_email = t_item.get("usuario_email", "")
                    u_nombre = t_item.get("usuario_nombre", u_email)
                    u_rol = t_item.get("usuario_rol", "Alumno")
                    u_fecha = t_item.get("ultimo_timestamp", "")[:16].replace("T", " ") if t_item.get("ultimo_timestamp") else ""
                    ultimo_txt = t_item.get("ultimo_texto", "")

                    card_t = ctk.CTkFrame(self.scroll_tickets, fg_color=COLOR_BG_CARD, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
                    card_t.pack(fill="x", padx=2, pady=3)

                    f_info = ctk.CTkFrame(card_t, fg_color="transparent")
                    f_info.pack(fill="x", padx=10, pady=8)

                    ctk.CTkLabel(f_info, text=f"👤 {u_nombre} ({u_rol})", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w")
                    ctk.CTkLabel(f_info, text=f"✉️ {u_email} • 🕒 {u_fecha}", font=("Segoe UI", 9), text_color=COLOR_ACCENT_CYAN).pack(anchor="w", pady=(1, 3))
                    ctk.CTkLabel(f_info, text=f"💬 \"{ultimo_txt[:60]}...\"", font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED, wraplength=260, justify="left").pack(anchor="w")

                    btn_abrir = ctk.CTkButton(
                        card_t, text="💬 Abrir Ticket", height=26, font=("Segoe UI", 10, "bold"),
                        fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                        command=lambda u=u_email, n=u_nombre, r=u_rol, msgs=t_item.get("mensajes", []): self._seleccionar_ticket(u, n, r, msgs)
                    )
                    btn_abrir.pack(fill="x", padx=10, pady=(0, 8))

            self.after(0, _render)

        threading.Thread(target=_thread, daemon=True).start()

    def _seleccionar_ticket(self, u_email: str, u_nombre: str, u_rol: str, mensajes: list):
        self._ticket_activo_email = u_email
        self.lbl_chat_usr_info.configure(text=f"🛡️ Conversación con: {u_nombre} ({u_email}) — {u_rol}", text_color=COLOR_TEXT_MAIN)
        self.btn_borrar_chat.pack(side="right", padx=10, pady=10)
        self.btn_enviar_resp.configure(state="normal")
        self.entry_resp_soporte.focus_set()

        for w in self.scroll_mensajes_soporte.winfo_children():
            w.destroy()

        for m in mensajes:
            es_soporte = m.get("es_soporte", False)
            emisor = "🛡️ Soporte Oficial" if es_soporte else f"👤 {m.get('emisor_nombre', u_nombre)}"
            hora = m.get("timestamp", "")[:19].replace("T", " ") if m.get("timestamp") else ""
            texto = m.get("texto", "")

            frame_b = ctk.CTkFrame(
                self.scroll_mensajes_soporte,
                fg_color="#065f46" if es_soporte else COLOR_BG_CARD,
                corner_radius=10,
                border_width=1,
                border_color="#10b981" if es_soporte else COLOR_BORDER
            )
            frame_b.pack(anchor="e" if es_soporte else "w", padx=8, pady=4)

            hdr = f"{emisor} • 🕒 {hora}"
            ctk.CTkLabel(frame_b, text=hdr, font=("Segoe UI", 9, "bold"),
                         text_color="#6ee7b7" if es_soporte else COLOR_TEXT_MUTED).pack(anchor="w", padx=10, pady=(6, 1))

            ctk.CTkLabel(frame_b, text=texto, font=("Segoe UI", 11),
                         text_color="#ffffff" if es_soporte else COLOR_TEXT_MAIN,
                         wraplength=420, justify="left").pack(anchor="w", padx=10, pady=(0, 8))

        self.scroll_mensajes_soporte._parent_canvas.yview_moveto(1.0)

    def _borrar_conversacion_ticket(self):
        if not self._ticket_activo_email:
            return
        
        usr = self._ticket_activo_email
        confirm = messagebox.askyesno(
            "🗑️ Vaciar Conversación",
            f"¿Estás seguro de que deseas ELIMINAR todo el historial de soporte con '{usr}'?\n\n"
            "• Se borrarán todos los mensajes cifrados de este ticket en Supabase.\n"
            "• Esta acción es permanente.\n\n"
            "¿Deseas continuar?"
        )
        if not confirm:
            return
        
        def _thread():
            ok, msg = admin_borrar_ticket_soporte(usr)
            if ok:
                def _exito():
                    self._ticket_activo_email = None
                    self.lbl_chat_usr_info.configure(text="Selecciona un ticket a la izquierda para responder", text_color=COLOR_TEXT_MUTED)
                    self.btn_enviar_resp.configure(state="disabled")
                    self.btn_borrar_chat.pack_forget()
                    for w in self.scroll_mensajes_soporte.winfo_children():
                        w.destroy()
                    self._cargar_tickets_soporte()
                    messagebox.showinfo("Conversación Eliminada", msg)
                self.after(0, _exito)
            else:
                self.after(0, lambda: messagebox.showerror("Error al borrar", msg))
        
        threading.Thread(target=_thread, daemon=True).start()

    def _enviar_respuesta_soporte(self):
        if not self._ticket_activo_email:
            return
        texto = self.entry_resp_soporte.get().strip()
        if not texto:
            return
        
        self.entry_resp_soporte.delete(0, "end")
        self.btn_enviar_resp.configure(state="disabled")

        def _thread():
            ok, res = admin_responder_ticket_soporte(self._ticket_activo_email, texto)
            if ok:
                ok2, tickets = admin_obtener_tickets_soporte()
                if ok2:
                    for t_item in tickets:
                        if t_item.get("usuario_email", "").lower() == self._ticket_activo_email.lower():
                            self.after(0, lambda: self._seleccionar_ticket(
                                self._ticket_activo_email, t_item.get("usuario_nombre", ""), t_item.get("usuario_rol", ""), t_item.get("mensajes", [])
                            ))
                            break
                    self.after(0, self._cargar_tickets_soporte)
            else:
                self.after(0, lambda: messagebox.showerror("Error Soporte", res))
            self.after(0, lambda: self.btn_enviar_resp.configure(state="normal"))

        threading.Thread(target=_thread, daemon=True).start()
