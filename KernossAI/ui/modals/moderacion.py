"""
KernossAI - Panel de Control y Moderación de Usuarios
Gestión de usuarios, sanciones disciplinarias, bloqueos por IP/HWID y visor de datos cifrados.
"""

import json
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
    admin_listar_usuarios,
    admin_aplicar_ban,
    admin_desbanear,
    admin_ver_mensajes_raw,
    admin_eliminar_usuario,
)


class VentanaAdminModeracion(ctk.CTkToplevel):
    """Panel de Control de Moderación, Hardware-Ban, IP-Ban y visualizador de Base de Datos Cifrada."""
    def __init__(self, parent, sesion):
        super().__init__(parent)
        self.parent = parent
        self.sesion = sesion
        self.title("👑 Panel Maestro de Moderación & Bans — KernossAI")
        self.geometry("980x740")
        self.minsize(800, 600)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        aplicar_icono(self)
        centrar_ventana(self, 980, 740)

        self._build_ui()
        self._cargar_usuarios()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, height=65, corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text="👑 Panel Maestro de Moderación & Bans",
                     font=("Segoe UI", 15, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=20, pady=16)

        btn_refrescar = ctk.CTkButton(header, text="🔄 Recargar Servidor", width=140, height=32,
                                      font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_PRIMARY,
                                      hover_color=COLOR_ACCENT_HOVER, command=self._cargar_usuarios)
        btn_refrescar.pack(side="right", padx=(10, 20))

        btn_cerrar = ctk.CTkButton(header, text="✕", width=36, height=36, fg_color=COLOR_BG_CARD,
                                   hover_color=COLOR_DANGER, font=("Segoe UI", 14, "bold"), command=self.destroy)
        btn_cerrar.pack(side="right", padx=6)

        self.tabview = ctk.CTkTabview(self, fg_color=COLOR_BG_DARK)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_usuarios = self.tabview.add("👥 Usuarios & Bans")
        self.tab_db_raw = self.tabview.add("🔒 Ver Base de Datos Cifrada")
        self.tab_ban_manual = self.tabview.add("🚫 Aplicar Ban Manual (IP / HWID)")
        self.tabview.set("👥 Usuarios & Bans")

        self._build_tab_usuarios()
        self._build_tab_db_raw()
        self._build_tab_ban_manual()

    def _build_tab_usuarios(self):
        frame_busqueda = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        frame_busqueda.pack(fill="x", padx=6, pady=(6, 8))

        self.entry_buscar_usr = ctk.CTkEntry(
            frame_busqueda, height=36, font=("Segoe UI", 11),
            placeholder_text="🔍 Buscar usuario por nombre, email, rol, IP o HWID...",
            fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER
        )
        self.entry_buscar_usr.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_buscar_usr.bind("<KeyRelease>", lambda e: self._filtrar_usuarios())

        btn_ip_ban_top = ctk.CTkButton(
            frame_busqueda, text="🌐 Banear IP Manual", width=140, height=36,
            font=("Segoe UI", 11, "bold"), fg_color="#7c3aed", hover_color="#6d28d9",
            command=self._ban_ip_manual_dialog
        )
        btn_ip_ban_top.pack(side="right")

        self.scroll_usr = ctk.CTkScrollableFrame(self.tab_usuarios, fg_color=COLOR_BG_DARK)
        self.scroll_usr.pack(fill="both", expand=True, padx=4, pady=4)
        self._lista_usuarios_cache = []

    def _build_tab_db_raw(self):
        frame_top = ctk.CTkFrame(self.tab_db_raw, fg_color="transparent")
        frame_top.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(frame_top, text="🔍 Contenido en bruto de 'mensajes' almacenado en el servidor:",
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

        btn_ver_raw = ctk.CTkButton(frame_top, text="📡 Consultar Raw", width=160, height=30,
                                    font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_CYAN,
                                    text_color="#000", hover_color="#38bdf8", command=self._cargar_raw_db)
        btn_ver_raw.pack(side="right")

        self.txt_raw = ctk.CTkTextbox(self.tab_db_raw, font=("Consolas", 11), wrap="word",
                                      fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        self.txt_raw.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_raw.insert("1.0", "Haz clic en 'Consultar Raw' para comprobar en vivo que los mensajes están cifrados en el servidor.")

    def _build_tab_ban_manual(self):
        frame = ctk.CTkFrame(self.tab_ban_manual, fg_color=COLOR_BG_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        frame.pack(fill="x", padx=30, pady=25)

        ctk.CTkLabel(frame, text="🚫 Bloqueo Manual de Usuarios, IP o Dispositivo Físico (HWID)",
                     font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkLabel(frame, text="Tipo de Sanción:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20)
        self.combo_tipo_ban = ctk.CTkComboBox(frame, values=["usuario", "ip", "hwid"], font=("Segoe UI", 11))
        self.combo_tipo_ban.pack(fill="x", padx=20, pady=(2, 10))

        ctk.CTkLabel(frame, text="Objetivo (Email / Dirección IP / HWID Hexadecimal):", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20)
        self.entry_ban_obj = ctk.CTkEntry(frame, font=("Segoe UI", 11), placeholder_text="ej: usuario@correo.com o 192.168.1.1 o 657ed7dbd298...")
        self.entry_ban_obj.pack(fill="x", padx=20, pady=(2, 10))

        ctk.CTkLabel(frame, text="Motivo del Baneo:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20)
        self.entry_ban_motivo = ctk.CTkEntry(frame, font=("Segoe UI", 11), placeholder_text="ej: Uso indebido del sistema o multicuentas")
        self.entry_ban_motivo.pack(fill="x", padx=20, pady=(2, 15))

        btn_ejecutar_ban = ctk.CTkButton(frame, text="⛔ Ejecutar Baneo Inmediato", height=38,
                                         font=("Segoe UI", 12, "bold"), fg_color=COLOR_DANGER,
                                         hover_color="#b91c1c", command=self._aplicar_ban_manual)
        btn_ejecutar_ban.pack(fill="x", padx=20, pady=(0, 20))

    def _cargar_usuarios(self):
        def _thread():
            ok, usuarios = admin_listar_usuarios()
            if not ok:
                self.after(0, lambda: messagebox.showerror("Error", "No se pudo conectar con el servidor."))
                return

            def _render():
                self._lista_usuarios_cache = usuarios or []
                self._filtrar_usuarios()

            self.after(0, _render)

        threading.Thread(target=_thread, daemon=True).start()

    def _filtrar_usuarios(self):
        for w in self.scroll_usr.winfo_children():
            w.destroy()

        filtro = self.entry_buscar_usr.get().strip().lower()
        usuarios = [
            u for u in self._lista_usuarios_cache
            if not filtro or
            filtro in u.get("email", "").lower() or
            filtro in u.get("nombre", "").lower() or
            filtro in u.get("rol", "").lower() or
            filtro in u.get("ip", "").lower() or
            filtro in u.get("hwid", "").lower()
        ]

        if not usuarios:
            msg = "🔍 No se encontraron usuarios que coincidan con la búsqueda." if filtro else "No hay usuarios registrados aún."
            ctk.CTkLabel(self.scroll_usr, text=msg, font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED).pack(pady=30)
            return

        for u in usuarios:
            email = u.get("email", "")
            nombre = u.get("nombre", "")
            rol = u.get("rol", "Alumno")
            ip = u.get("ip", "N/D")
            hwid = u.get("hwid", "N/D")
            baneado = u.get("baneado", False)
            ip_baneada = u.get("ip_baneada", False)
            hwid_baneado = u.get("hwid_baneado", False)

            card = ctk.CTkFrame(self.scroll_usr, fg_color=COLOR_BG_CARD, corner_radius=10, border_width=1,
                                border_color=COLOR_DANGER if (baneado or ip_baneada or hwid_baneado) else COLOR_BORDER)
            card.pack(fill="x", padx=6, pady=4)

            f_info = ctk.CTkFrame(card, fg_color="transparent")
            f_info.pack(side="left", padx=12, pady=10, fill="x", expand=True)

            status_str = "⛔ BANEADO" if baneado else "🟢 ACTIVO"
            ctk.CTkLabel(f_info, text=f"{nombre} ({email}) — {rol} [{status_str}]",
                         font=("Segoe UI", 12, "bold"),
                         text_color=COLOR_DANGER if baneado else COLOR_TEXT_MAIN).pack(anchor="w")

            det = f"🌐 IP: {ip} {'(IP-BANEADA)' if ip_baneada else ''}  |  💻 HWID: {hwid[:16]}... {'(HWID-BANEADO)' if hwid_baneado else ''}"
            ctk.CTkLabel(f_info, text=det, font=("Segoe UI", 10), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(2, 0))

            f_actions = ctk.CTkFrame(card, fg_color="transparent")
            f_actions.pack(side="right", padx=10, pady=10)

            if not baneado:
                ctk.CTkButton(f_actions, text="🚫 Ban Cuenta", width=90, height=28,
                              font=("Segoe UI", 10, "bold"), fg_color=COLOR_DANGER, hover_color="#b91c1c",
                              command=lambda em=email: self._ban_quick(em, "usuario")).pack(side="left", padx=2)
            else:
                ctk.CTkButton(f_actions, text="✅ Desban Cuenta", width=105, height=28,
                              font=("Segoe UI", 10, "bold"), fg_color=COLOR_SUCCESS, hover_color="#15803d",
                              command=lambda em=email: self._desban_quick(em, "usuario")).pack(side="left", padx=2)

            if not ip_baneada:
                ctk.CTkButton(f_actions, text="🌐 IP-Ban", width=75, height=28,
                              font=("Segoe UI", 10, "bold"), fg_color="#7c3aed", hover_color="#6d28d9",
                              command=lambda ip_val=ip, em=email: self._ip_ban_user(ip_val, em)).pack(side="left", padx=2)
            else:
                ctk.CTkButton(f_actions, text="✅ Desban IP", width=85, height=28,
                              font=("Segoe UI", 10, "bold"), fg_color=COLOR_SUCCESS, hover_color="#15803d",
                              command=lambda ip_val=ip: self._desban_quick(ip_val, "ip")).pack(side="left", padx=2)

            if not hwid_baneado and hwid != "N/D" and hwid != "HWID_NO_REPORTADO":
                ctk.CTkButton(f_actions, text="💻 HW-Ban", width=75, height=28,
                              font=("Segoe UI", 10, "bold"), fg_color="#b45309", hover_color="#92400e",
                              command=lambda hw=hwid: self._ban_quick(hw, "hwid")).pack(side="left", padx=2)
            elif hwid_baneado:
                ctk.CTkButton(f_actions, text="✅ Desban HW", width=85, height=28,
                              font=("Segoe UI", 10, "bold"), fg_color=COLOR_SUCCESS, hover_color="#15803d",
                              command=lambda hw=hwid: self._desban_quick(hw, "hwid")).pack(side="left", padx=2)

            ctk.CTkButton(f_actions, text="🗑️", width=30, height=28,
                          font=("Segoe UI", 10), fg_color="#7f1d1d", hover_color="#991b1b",
                          command=lambda em=email: self._eliminar_usuario_admin(em)).pack(side="left", padx=2)

    def _ban_ip_manual_dialog(self):
        dialogo = ctk.CTkInputDialog(
            text="Introduce la dirección IP pública que deseas bloquear del sistema:",
            title="🌐 Banear Dirección IP"
        )
        ip_ingresada = dialogo.get_input()
        if not ip_ingresada:
            return
        ip_limpia = ip_ingresada.strip()

        dialogo_motivo = ctk.CTkInputDialog(
            text=f"Introduce el motivo de la sanción para la IP {ip_limpia}:",
            title="📋 Motivo de Sanción IP"
        )
        motivo = dialogo_motivo.get_input()
        motivo_limpio = (motivo or "").strip() or "Bloqueo de red por administración"

        def _thread():
            ok, res = admin_aplicar_ban(ip_limpia, "ip", motivo_limpio)
            if ok:
                self.after(0, lambda: messagebox.showinfo("IP Baneada", f"Se ha bloqueado la IP '{ip_limpia}'.\n{res}"))
                self._cargar_usuarios()
            else:
                self.after(0, lambda: messagebox.showerror("Error", res))

        threading.Thread(target=_thread, daemon=True).start()

    def _ip_ban_user(self, ip_val: str, email: str):
        if ip_val in ("N/D", "", "127.0.0.1"):
            messagebox.showwarning("Atención", "El usuario no tiene una IP pública válida registrada.")
            return

        dialogo = ctk.CTkInputDialog(
            text=f"Introduce el motivo del IP-Ban para '{ip_val}' ({email}):",
            title=f"🌐 IP-Ban a {email}"
        )
        motivo = dialogo.get_input()
        if motivo is None:
            return
        motivo_limpio = motivo.strip() or f"Sanción disciplinaria asociada a la cuenta {email}"

        def _thread():
            ok, res = admin_aplicar_ban(ip_val, "ip", motivo_limpio)
            if ok:
                self.after(0, lambda: messagebox.showinfo("IP Bloqueada", f"Se ha bloqueado la IP '{ip_val}'.\n{res}"))
                self._cargar_usuarios()
            else:
                self.after(0, lambda: messagebox.showerror("Error", res))

        threading.Thread(target=_thread, daemon=True).start()

    def _eliminar_usuario_admin(self, email: str):
        confirm = messagebox.askyesno(
            "🗑️ Eliminar Usuario",
            f"¿Estás seguro de que deseas ELIMINAR al usuario '{email}' de la base de datos?\n\n"
            "Esta acción es permanente.",
            icon="warning"
        )
        if not confirm:
            return

        def _thread():
            ok, res = admin_eliminar_usuario(email)
            if ok:
                self.after(0, lambda: messagebox.showinfo("Usuario Eliminado", res))
                self._cargar_usuarios()
            else:
                self.after(0, lambda: messagebox.showerror("Error", res))

        threading.Thread(target=_thread, daemon=True).start()

    def _ban_quick(self, objetivo: str, tipo: str):
        dialogo = ctk.CTkInputDialog(
            text=f"Introduce el motivo de la sanción para {tipo} '{objetivo}':\n(Se mostrará al usuario en su pantalla roja de bloqueo)",
            title=f"⛔ Motivo del Baneo de {tipo.upper()}"
        )
        motivo = dialogo.get_input()
        if motivo is None:
            return

        motivo_limpio = motivo.strip() or "Infracción de las normas del sistema"
        ok, res = admin_aplicar_ban(objetivo, tipo, motivo_limpio)
        if ok:
            messagebox.showinfo("Baneo Aplicado", f"{res}\n\n📋 Motivo: {motivo_limpio}")
            self._cargar_usuarios()
        else:
            messagebox.showerror("Error", res)

    def _desban_quick(self, objetivo: str, tipo: str):
        ok, res = admin_desbanear(objetivo, tipo)
        if ok:
            messagebox.showinfo("Desbaneo Aplicado", res)
            self._cargar_usuarios()
        else:
            messagebox.showerror("Error", res)

    def _aplicar_ban_manual(self):
        tipo = self.combo_tipo_ban.get()
        obj = self.entry_ban_obj.get().strip()
        motivo = self.entry_ban_motivo.get().strip() or "Infracción de normas"
        if not obj:
            messagebox.showwarning("Atención", "Escribe el objetivo a banear.")
            return

        ok, res = admin_aplicar_ban(obj, tipo, motivo)
        if ok:
            messagebox.showinfo("Baneo Exitoso", res)
            self.entry_ban_obj.delete(0, "end")
            self._cargar_usuarios()
        else:
            messagebox.showerror("Error", res)

    def _cargar_raw_db(self):
        self.txt_raw.delete("1.0", "end")
        self.txt_raw.insert("1.0", "⏳ Consultando base de datos cifrada (Zero-Knowledge)...")

        def _thread():
            ok, res = admin_ver_mensajes_raw()
            if ok:
                txt = json.dumps(res, ensure_ascii=False, indent=2)
                self.after(0, lambda: (self.txt_raw.delete("1.0", "end"), self.txt_raw.insert("1.0", txt)))
            else:
                err_msg = res.get("error", "Error al consultar la base de datos.") if isinstance(res, dict) else "Error al consultar la base de datos."
                self.after(0, lambda: (self.txt_raw.delete("1.0", "end"), self.txt_raw.insert("1.0", f"❌ {err_msg}")))

        threading.Thread(target=_thread, daemon=True).start()
