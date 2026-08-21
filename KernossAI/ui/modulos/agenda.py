"""
KernossAI - Módulo: Agenda y Calendario de Estudio
Gestión de fechas de exámenes, entregas, eventos académicos y persistencia local.
"""

import os
import json
import calendar
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

from KernossAI.core.theme import (
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
    COLOR_SUCCESS,
    COLOR_SUCCESS_HOVER,
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
)
from KernossAI.core.i18n import t, obtener_idioma_activo


class ModuloCalendario(ctk.CTkFrame):
    """Módulo de organización y agenda académica reactiva."""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.ruta_datos = os.path.expanduser("~/.agenda_estudios.json")
        self.eventos = self._cargar_eventos()
        self.hoy = datetime.now()
        self.año_actual = self.hoy.year
        self.mes_actual = self.hoy.month
        self.dia_seleccionado = f"{self.año_actual}-{self.mes_actual:02d}-{self.hoy.day:02d}"
        meses_por_idioma = {
            "es": ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
            "en": ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            "de": ["", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
            "fr": ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        }
        self.nombres_meses = meses_por_idioma.get(obtener_idioma_activo(), meses_por_idioma["es"])
        self.botones_dias = []
        self._build_ui()
        self._actualizar_calendario()
        self._cargar_evento_en_editor()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        frame_izq = ctk.CTkFrame(self, fg_color="transparent")
        frame_izq.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame_nav = ctk.CTkFrame(frame_izq, fg_color=COLOR_BG_CARD, height=60, corner_radius=12,
                                      border_width=1, border_color=COLOR_BORDER)
        self.frame_nav.pack(fill="x", pady=(0, 15))
        self.frame_nav.pack_propagate(False)
        ctk.CTkButton(self.frame_nav, text="◀", width=40, font=("Segoe UI", 16),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      command=self._mes_anterior).pack(side="left", padx=15, pady=10)
        self.lbl_mes_año = ctk.CTkLabel(self.frame_nav, text="", font=("Segoe UI", 20, "bold"),
                                         text_color=COLOR_ACCENT_SKY)
        self.lbl_mes_año.pack(side="left", expand=True)
        ctk.CTkButton(self.frame_nav, text="▶", width=40, font=("Segoe UI", 16),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      command=self._mes_siguiente).pack(side="right", padx=15, pady=10)

        self.frame_dias = ctk.CTkFrame(frame_izq, fg_color=COLOR_BG_CARD, corner_radius=15,
                                        border_width=1, border_color=COLOR_BORDER)
        self.frame_dias.pack(fill="both", expand=True)
        for i in range(7):
            self.frame_dias.grid_columnconfigure(i, weight=1, uniform="dias")
        for i in range(7):
            self.frame_dias.grid_rowconfigure(i, weight=1, uniform="semanas")

        dias_semana_por_idioma = {
            "es": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
            "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "de": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
            "fr": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        }
        lista_dias = dias_semana_por_idioma.get(obtener_idioma_activo(), dias_semana_por_idioma["es"])
        for col, dia in enumerate(lista_dias):
            ctk.CTkLabel(self.frame_dias, text=dia, font=("Segoe UI", 13, "bold"),
                         text_color=COLOR_ACCENT_CYAN).grid(row=0, column=col, pady=8, sticky="nsew")

        frame_der = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=15,
                                 border_width=1, border_color=COLOR_BORDER)
        frame_der.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        ctk.CTkLabel(frame_der, text=t("agenda_titulo"), font=("Segoe UI", 16, "bold"),
                     text_color=COLOR_ACCENT_SKY).pack(pady=(25, 5), padx=20, anchor="w")
        self.lbl_fecha_actual = ctk.CTkLabel(frame_der, text="", font=("Segoe UI", 13), text_color=COLOR_TEXT_MUTED)
        self.lbl_fecha_actual.pack(pady=(0, 15), padx=20, anchor="w")
        self.txt_tareas = ctk.CTkTextbox(frame_der, font=("Segoe UI", 13), border_width=1,
                                         fg_color=COLOR_BG_CARD_LIGHT, border_color=COLOR_BORDER)
        self.txt_tareas.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(frame_der, text=t("apunt_btn_guardar"), font=("Segoe UI", 13, "bold"),
                      fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
                      command=self._guardar_evento).pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkButton(frame_der, text=t("apunt_btn_borrar"), font=("Segoe UI", 13),
                      fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER,
                      command=self._borrar_evento).pack(fill="x", padx=20, pady=(5, 25))

    def _actualizar_calendario(self):
        for btn in self.botones_dias:
            btn.destroy()
        self.botones_dias.clear()
        self.lbl_mes_año.configure(text=f"{self.nombres_meses[self.mes_actual]} {self.año_actual}")
        primer_dia_semana, dias_en_mes = calendar.monthrange(self.año_actual, self.mes_actual)
        fila = 1
        columna = primer_dia_semana
        for dia in range(1, dias_en_mes + 1):
            fecha_clave = f"{self.año_actual}-{self.mes_actual:02d}-{dia:02d}"
            esta_sel = (fecha_clave == self.dia_seleccionado)
            es_hoy = (self.hoy.year == self.año_actual and self.hoy.month == self.mes_actual and self.hoy.day == dia)
            tiene_tareas = fecha_clave in self.eventos and self.eventos[fecha_clave].strip()
            if esta_sel:
                fg = COLOR_ACCENT_PRIMARY
                tc = "white"
            elif es_hoy:
                fg = COLOR_ACCENT_CYAN
                tc = "white"
            elif tiene_tareas:
                fg = "#064e3b"
                tc = "#6ee7b7"
            else:
                fg = COLOR_BG_CARD_LIGHT
                tc = COLOR_TEXT_MAIN
            btn = ctk.CTkButton(self.frame_dias, text=str(dia), font=("Segoe UI", 12, "bold" if (es_hoy or tiene_tareas) else "normal"),
                                fg_color=fg, hover_color=COLOR_ACCENT_HOVER, text_color=tc,
                                corner_radius=8, command=lambda d=dia: self._seleccionar_dia(d))
            btn.grid(row=fila, column=columna, padx=4, pady=4, sticky="nsew")
            self.botones_dias.append(btn)
            columna += 1
            if columna > 6:
                columna = 0
                fila += 1

    def _seleccionar_dia(self, dia):
        self.dia_seleccionado = f"{self.año_actual}-{self.mes_actual:02d}-{dia:02d}"
        self._actualizar_calendario()
        self._cargar_evento_en_editor()

    def _mes_anterior(self):
        self.mes_actual -= 1
        if self.mes_actual < 1:
            self.mes_actual = 12
            self.año_actual -= 1
        self._actualizar_calendario()

    def _mes_siguiente(self):
        self.mes_actual += 1
        if self.mes_actual > 12:
            self.mes_actual = 1
            self.año_actual += 1
        self._actualizar_calendario()

    def _cargar_eventos(self):
        if os.path.exists(self.ruta_datos):
            try:
                with open(self.ruta_datos, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _cargar_evento_en_editor(self):
        partes = self.dia_seleccionado.split("-")
        fecha_objeto = datetime(int(partes[0]), int(partes[1]), int(partes[2]))
        self.lbl_fecha_actual.configure(text=fecha_objeto.strftime("%d de %B de %Y").title())
        self.txt_tareas.delete("1.0", "end")
        if self.dia_seleccionado in self.eventos:
            self.txt_tareas.insert("1.0", self.eventos[self.dia_seleccionado])

    def _guardar_evento(self):
        contenido = self.txt_tareas.get("1.0", "end-1c").strip()
        if contenido:
            self.eventos[self.dia_seleccionado] = contenido
        elif self.dia_seleccionado in self.eventos:
            del self.eventos[self.dia_seleccionado]
        try:
            with open(self.ruta_datos, 'w', encoding='utf-8') as f:
                json.dump(self.eventos, f, ensure_ascii=False, indent=2)
            self._actualizar_calendario()
            messagebox.showinfo("Guardado", "Agenda actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _borrar_evento(self):
        if self.dia_seleccionado in self.eventos:
            if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar todas las tareas de este día?"):
                del self.eventos[self.dia_seleccionado]
                self.txt_tareas.delete("1.0", "end")
                with open(self.ruta_datos, 'w', encoding='utf-8') as f:
                    json.dump(self.eventos, f, ensure_ascii=False, indent=2)
                self._actualizar_calendario()
