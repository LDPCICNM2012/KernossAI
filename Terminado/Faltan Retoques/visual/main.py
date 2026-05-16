import customtkinter as ctk
from PIL import Image # Asegúrate de tener 'pip install pillow'
import subprocess
import os
import sys

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DashboardEstudios(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Immune Study Suite 2026 - Dashboard")
        self.geometry("900x600")
        self.resizable(False, False)

        # Configuración de layout
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
            text="Suite de Herramientas de Alto Rendimiento • Lander Edition", 
            font=("Segoe UI", 12),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 20))

        # ───── CONTENEDOR DE BOTONES ─────
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.grid(row=1, column=0, padx=40, pady=40, sticky="nsew")
        
        # 2 columnas y 2 filas para los botones principales
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)
        self.grid_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Definición de botones (Texto, Archivo, Color)
        herramientas = [
            ("📝 Apuntador de Notas", "Apuntador_Notas_Visual.py", "#3498db"),
            ("🔍 Resumidor de Textos", "resumidor_de_textos_visual.py", "#9b59b6"),
            ("🛠️ Solucionador IA", "Ayudador_de_problemas_visual.py", "#e67e22"),
            ("🚀 Generador de Exámenes", "generador_examen_visual.py", "#e74c3c"),
            ("📊 Calculadora de Medias", "Calculador_Notas_Tkinter_FINAL.py", "#2ecc71")
        ]

        # Crear los botones dinámicamente
        for i, (nombre, archivo, color) in enumerate(herramientas):
            row = i // 2
            col = i % 2
            
            # Si es el último botón y está solo, que ocupe las dos columnas
            columnspan = 2 if i == len(herramientas)-1 else 1
            
            btn = ctk.CTkButton(
                self.grid_frame,
                text=nombre,
                font=("Segoe UI", 16, "bold"),
                height=100,
                fg_color=color,
                hover_color=self.darken_color(color),
                command=lambda a=archivo: self.lanzar_herramienta(a)
            )
            btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew", columnspan=columnspan)

        # ───── FOOTER ─────
        self.footer = ctk.CTkLabel(
            self, 
            text="© 2026 Lander S.L & Immune Technology Institute • Todos los derechos reservados",
            font=("Segoe UI", 10),
            text_color="gray"
        )
        self.footer.grid(row=2, column=0, pady=10)

    def darken_color(self, hex_color):
        """Función estética para generar el color hover automáticamente"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        dark_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*dark_rgb)

    def lanzar_herramienta(self, nombre_archivo):
        """Lanza el script de Python en un proceso independiente"""
        # Obtenemos la ruta absoluta de la carpeta donde está este main.py
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_script = os.path.join(directorio_actual, nombre_archivo)

        if os.path.exists(ruta_script):
            try:
                # Ejecutamos con el mismo intérprete de python que el main
                subprocess.Popen([sys.executable, ruta_script])
            except Exception as e:
                print(f"Error al lanzar {nombre_archivo}: {e}")
        else:
            print(f"No se encontró el archivo: {ruta_script}")

if __name__ == "__main__":
    app = DashboardEstudios()
    app.mainloop() 