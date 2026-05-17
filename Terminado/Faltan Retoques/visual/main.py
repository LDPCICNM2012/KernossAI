import sys
import os

# ───── ENRUTADOR MÁGICO PARA PYINSTALLER (MAC) ─────
if getattr(sys, 'frozen', False) and len(sys.argv) > 1:
    script_a_abrir = sys.argv[1]
    ruta_interna = os.path.join(sys._MEIPASS, script_a_abrir)

    if os.path.exists(ruta_interna):
        try:
            with open(ruta_interna, 'r', encoding='utf-8') as f:
                codigo = f.read()
            exec(codigo, {'__name__': '__main__', '__file__': ruta_interna})
        except Exception as e:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error al abrir módulo", f"{script_a_abrir}\n\n{e}")
            root.destroy()
    else:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Módulo no encontrado", f"No se encontró:\n{ruta_interna}")
        root.destroy()

    sys.exit(0)
# ───────────────────────────────────────────────────

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import subprocess

# Configuración estética global de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DashboardEstudios(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Immune Study Suite 2026 - Dashboard")
        self.geometry("1200x680")
        self.resizable(False, False)

        self.procesos_activos = []
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar_ventana)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ───── CABECERA ─────
        self.header = ctk.CTkFrame(self, height=100, fg_color="#1a1a1a", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header,
            text="IMMUNE TECHNOLOGY INSTITUTE",
            font=("Segoe UI", 24, "bold"),
            text_color="#64b5f6"
        )
        self.title_label.pack(pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.header,
            text="Suite de Herramientas de Alto Rendimiento • Beta Testing Edition",
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 15))

        # ───── GRID DE TARJETAS ─────
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.grid(row=1, column=0, padx=30, pady=15, sticky="nsew")

        self.grid_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        self.grid_frame.grid_rowconfigure((0, 1), weight=1, uniform="equal")

        self.apps = [
            {
                "titulo": "Calculadora de Medias",
                "desc": "Calcula promedios simples y ponderados divididos por bloques internos al 100%.",
                "color": "#1e88e5",
                "script": "Calculador_Notas_Tkinter_FINAL.py"
            },
            {
                "titulo": "Apuntador de Notas",
                "desc": "Editor de texto nativo para guardar apuntes de clases y exportarlos a Word.",
                "color": "#43a047",
                "script": "Apuntador_Notas_Visual.py"
            },
            {
                "titulo": "Resumidor Académico IA",
                "desc": "Genera extensos resúmenes de tus temas utilizando modelos locales de Ollama.",
                "color": "#e53935",
                "script": "resumidor_de_textos_visual.py"
            },
            {
                "titulo": "Generador de Exámenes IA",
                "desc": "Genera evaluaciones personalizadas de opción múltiple y desarrollo mediante IA.",
                "color": "#8e24aa",
                "script": "generador_examen_visual.py"
            },
            {
                "titulo": "Ayudador de Problemas IA",
                "desc": "Analiza problemas complejos, identifica causas raíz y genera soluciones técnicas paso a paso.",
                "color": "#00acc1",
                "script": "Ayudador_de_problemas_visual.py"
            }
        ]

        for index, app in enumerate(self.apps):
            row = index // 3
            col = index % 3
            self.crear_tarjeta(self.grid_frame, app, row, col)

        # ───── BOTÓN SALIR ─────
        self.btn_salir_suite = ctk.CTkButton(
            self,
            text="Cerrar Suite Completa",
            font=("Segoe UI", 13, "bold"),
            fg_color="#c62828",
            hover_color="#9e1c1c",
            text_color="white",
            height=40,
            corner_radius=10,
            command=self.al_cerrar_ventana
        )
        self.btn_salir_suite.grid(row=2, column=0, padx=45, pady=(10, 5), sticky="ew")

        self.footer = ctk.CTkLabel(
            self,
            text="© 2026 Lander S.L & Immune Technology Institute • Todos los derechos reservados",
            font=("Segoe UI", 10),
            text_color="gray"
        )
        self.footer.grid(row=3, column=0, pady=(5, 10))

    def darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        dark_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*dark_rgb)

    def crear_tarjeta(self, parent, app_data, row, col):
        hover_c = self.darken_color(app_data["color"])

        card = ctk.CTkFrame(
            parent,
            corner_radius=15,
            border_width=1,
            border_color=["#e0e0e0", "#2d2d2d"],
            fg_color=["#ffffff", "#242424"]
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        lbl_title = ctk.CTkLabel(card, text=app_data["titulo"], font=("Segoe UI", 18, "bold"), text_color=app_data["color"])
        lbl_title.pack(pady=(20, 5), padx=20, anchor="w")

        lbl_desc = ctk.CTkLabel(card, text=app_data["desc"], font=("Segoe UI", 12), text_color=["#666666", "#aaaaaa"], wraplength=320, justify="left")
        lbl_desc.pack(pady=(0, 20), padx=20, anchor="w", fill="x", expand=True)

        btn_abrir = ctk.CTkButton(
            card,
            text="Iniciar Módulo",
            font=("Segoe UI", 12, "bold"),
            fg_color=app_data["color"],
            hover_color=hover_c,
            text_color="white",
            height=35,
            corner_radius=8,
            command=lambda s=app_data["script"]: self.lanzar_herramienta(s)
        )
        btn_abrir.pack(pady=(0, 20), padx=20, fill="x")

    def lanzar_herramienta(self, nombre_archivo):
        try:
            if getattr(sys, 'frozen', False):
                # En una app compilada de PyInstaller en macOS,
                # usamos el propio ejecutable pasando el script como argumento.
                exe_path = sys.executable

                # En macOS .app, a veces sys.executable apunta al Python del sistema.
                # Nos aseguramos de usar el binario real del bundle.
                bundle_exe = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))),
                    "MacOS",
                    "Immune Study Suite"
                )
                if os.path.isfile(bundle_exe):
                    exe_path = bundle_exe

                env = os.environ.copy()
                # Pasamos _MEIPASS al subproceso para que el enrutador lo encuentre
                if hasattr(sys, '_MEIPASS'):
                    env['_MEIPASS2'] = sys._MEIPASS

                proceso = subprocess.Popen([exe_path, nombre_archivo], env=env)
            else:
                # Ejecución normal desde VS Code / terminal
                ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
                proceso = subprocess.Popen([sys.executable, ruta])

            self.procesos_activos.append(proceso)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir:\n{e}")

    def al_cerrar_ventana(self):
        for proceso in self.procesos_activos:
            if proceso.poll() is None:
                try:
                    proceso.kill()
                except Exception:
                    pass

        self.quit()
        self.destroy()
        os._exit(0)

if __name__ == "__main__":
    app = DashboardEstudios()
    app.mainloop()