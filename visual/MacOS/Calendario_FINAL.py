import customtkinter as ctk
from tkinter import messagebox
import json
import os
import calendar
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CalendarioEstudios(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Agenda y Calendario de Estudios")
        self.geometry("1000x750")
        self.resizable(False, False)

        # 1. Persistencia de Datos (Estilo Bloc de Notas)
        self.ruta_datos = os.path.expanduser("~/.agenda_estudios.json")
        self.eventos = self.cargar_eventos()

        # 2. Control del tiempo basado en el Dispositivo
        self.hoy = datetime.now()
        self.año_actual = self.hoy.year
        self.mes_actual = self.hoy.month
        self.dia_seleccionado = f"{self.año_actual}-{self.mes_actual:02d}-{self.hoy.day:02d}"

        # Nombres de los meses en español
        self.nombres_meses = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        # Matriz para guardar las referencias de los botones del calendario
        self.botones_dias = []

        self.setup_ui()
        self.actualizar_calendario()
        self.cargar_evento_en_editor()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=2) # Zona Calendario (izq)
        self.grid_columnconfigure(1, weight=1) # Zona Tareas (der)
        self.grid_rowconfigure(0, weight=1)

        # ──────── PANEL IZQUIERDO: CALENDARIO ────────
        self.frame_izquierdo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_izquierdo.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Cabecera de navegación (Mes / Año y flechas)
        self.frame_nav = ctk.CTkFrame(self.frame_izquierdo, fg_color="#1a1a1a", height=60, corner_radius=10)
        self.frame_nav.pack(fill="x", pady=(0, 15))
        self.frame_nav.pack_propagate(False)

        self.btn_ant = ctk.CTkButton(self.frame_nav, text="◀", width=40, font=("Segoe UI", 16), command=self.mes_anterior)
        self.btn_ant.pack(side="left", padx=15, pady=10)

        self.lbl_mes_año = ctk.CTkLabel(self.frame_nav, text="", font=("Segoe UI", 20, "bold"), text_color="#64b5f6")
        self.lbl_mes_año.pack(side="left", expand=True)

        self.btn_sig = ctk.CTkButton(self.frame_nav, text="▶", width=40, font=("Segoe UI", 16), command=self.mes_siguiente)
        self.btn_sig.pack(side="right", padx=15, pady=10)

        # Rejilla para los días de la semana y del mes
        self.frame_dias = ctk.CTkFrame(self.frame_izquierdo, fg_color="#242424", corner_radius=15, border_width=1, border_color="#2d2d2d")
        self.frame_dias.pack(fill="both", expand=True)

        # Configurar 7 columnas uniformes (Lunes a Domingo)
        for i in range(7):
            self.frame_dias.grid_columnconfigure(i, weight=1, uniform="dias")
        # 1 fila para cabecera + 6 filas para cubrir cualquier estructura de mes
        for i in range(7):
            self.frame_dias.grid_rowconfigure(i, weight=1, uniform="semanas")

        # Nombres de días de la semana
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for col, dia in enumerate(dias_semana):
            lbl = ctk.CTkLabel(self.frame_dias, text=dia, font=("Segoe UI", 13, "bold"), text_color="gray")
            lbl.grid(row=0, column=col, pady=5, sticky="nsew")

        # ──────── PANEL DERECHO: EDITOR DE EVENTOS ────────
        self.frame_derecho = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.frame_derecho.grid(row=0, column=1, sticky="nsew")

        self.lbl_fecha_top = ctk.CTkLabel(self.frame_derecho, text="Tareas del día", font=("Segoe UI", 18, "bold"), text_color="#64b5f6")
        self.lbl_fecha_top.pack(pady=(25, 5), padx=20, anchor="w")

        self.lbl_fecha_actual = ctk.CTkLabel(self.frame_derecho, text="", font=("Segoe UI", 14), text_color="gray")
        self.lbl_fecha_actual.pack(pady=(0, 15), padx=20, anchor="w")

        # Editor de texto libre para anotar las tareas de ese día
        self.txt_tareas = ctk.CTkTextbox(self.frame_derecho, font=("Segoe UI", 13), border_width=1, border_color="#3d3d3d")
        self.txt_tareas.pack(fill="both", expand=True, padx=20, pady=10)

        self.btn_guardar = ctk.CTkButton(
            self.frame_derecho, 
            text="Guardar Cambios", 
            font=("Segoe UI", 13, "bold"), 
            fg_color="#2e7d32", 
            hover_color="#1b5e20",
            command=self.guardar_evento_actual
        )
        self.btn_guardar.pack(fill="x", padx=20, pady=(10, 5))

        self.btn_limpiar = ctk.CTkButton(
            self.frame_derecho, 
            text="Borrar Todo", 
            font=("Segoe UI", 13), 
            fg_color="#c62828", 
            hover_color="#b71c1c",
            command=self.borrar_evento_actual
        )
        self.btn_limpiar.pack(fill="x", padx=20, pady=(5, 25))

    # ──────── LÓGICA MATEMÁTICA DEL CALENDARIO ────────
    def actualizar_calendario(self):
        # Limpiar los botones pintados del mes anterior
        for btn in self.botones_dias:
            btn.destroy()
        self.botones_dias.clear()

        # Actualizar título de cabecera
        self.lbl_mes_año.configure(text=f"{self.nombres_meses[self.mes_actual]} {self.año_actual}")

        # calendar.monthrange devuelve: (primer_dia_semana_del_mes [0=Lun], cantidad_dias_mes)
        primer_dia_semana, dias_en_mes = calendar.monthrange(self.año_actual, self.mes_actual)

        fila = 1
        columna = primer_dia_semana

        for dia in range(1, dias_en_mes + 1):
            fecha_clave = f"{self.año_actual}-{self.mes_actual:02d}-{dia:02d}"

            # Definir colores estéticos
            esta_seleccionado = (fecha_clave == self.dia_seleccionado)
            es_hoy = (self.hoy.year == self.año_actual and self.hoy.month == self.mes_actual and self.hoy.day == dia)
            tiene_tareas = fecha_clave in self.eventos and self.eventos[fecha_clave].strip()

            # Configuración dinámica del color del botón
            if esta_seleccionado:
                fg = "#1565c0"       # Azul fuerte si está seleccionado
                text_color = "white"
            elif es_hoy:
                fg = "#0d47a1"       # Azul oscuro para remarcar "Hoy"
                text_color = "#64b5f6"
            elif tiene_tareas:
                fg = "#1e4620"       # Verde sutil para avisar que hay eventos apuntados
                text_color = "#81c784"
            else:
                fg = "#333333"       # Color gris neutro por defecto
                text_color = "white"

            btn_dia = ctk.CTkButton(
                self.frame_dias,
                text=str(dia),
                font=("Segoe UI", 12, "bold" if (es_hoy or tiene_tareas) else "normal"),
                fg_color=fg,
                hover_color="#444444",
                text_color=text_color,
                corner_radius=8,
                command=lambda d=dia: self.seleccionar_dia(d)
            )
            btn_dia.grid(row=fila, column=columna, padx=4, pady=4, sticky="nsew")
            self.botones_dias.append(btn_dia)

            columna += 1
            if columna > 6:
                columna = 0
                fila += 1

    def seleccionar_dia(self, dia):
        self.dia_seleccionado = f"{self.año_actual}-{self.mes_actual:02d}-{dia:02d}"
        self.actualizar_calendario()
        self.cargar_evento_en_editor()

    def mes_anterior(self):
        self.mes_actual -= 1
        if self.mes_actual < 1:
            self.mes_actual = 12
            self.año_actual -= 1
        self.actualizar_calendario()

    def mes_siguiente(self):
        self.mes_actual += 1
        if self.mes_actual > 12:
            self.mes_actual = 1
            self.año_actual += 1
        self.actualizar_calendario()

    # ──────── LÓGICA DE PERSISTENCIA (JSON) ────────
    def cargar_eventos(self):
        if os.path.exists(self.ruta_datos):
            try:
                with open(self.ruta_datos, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def cargar_evento_en_editor(self):
        # Formatear la cabecera del editor
        partes = self.dia_seleccionado.split("-")
        fecha_objeto = datetime(int(partes[0]), int(partes[1]), int(partes[2]))
        self.lbl_fecha_actual.configure(text=fecha_objeto.strftime("%d de %B de %Y").title())

        # Cargar texto si existe
        self.txt_tareas.delete("1.0", "end")
        if self.dia_seleccionado in self.eventos:
            self.txt_tareas.insert("1.0", self.eventos[self.dia_seleccionado])

    def guardar_evento_actual(self):
        contenido = self.txt_tareas.get("1.0", "end-1c").strip()
        if contenido:
            self.eventos[self.dia_seleccionado] = contenido
        else:
            if self.dia_seleccionado in self.eventos:
                del self.eventos[self.dia_seleccionado]

        try:
            with open(self.ruta_datos, 'w', encoding='utf-8') as f:
                json.dump(self.eventos, f, ensure_ascii=False, indent=2)
            self.actualizar_calendario()
            messagebox.showinfo("Guardado", "Agenda actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def borrar_evento_actual(self):
        if self.dia_seleccionado in self.eventos:
            if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar todas las tareas de este día?"):
                del self.eventos[self.dia_seleccionado]
                self.txt_tareas.delete("1.0", "end")
                with open(self.ruta_datos, 'w', encoding='utf-8') as f:
                    json.dump(self.eventos, f, ensure_ascii=False, indent=2)
                self.actualizar_calendario()

if __name__ == "__main__":
    app = CalendarioEstudios()
    app.mainloop()