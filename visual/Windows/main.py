import sys
import os
import subprocess


# ───── ENRUTADOR MÁGICO PARA PYINSTALLER (WINDOWS Y MAC) ─────
if getattr(sys, 'frozen', False) and len(sys.argv) > 1:
    script_a_abrir = sys.argv[1]
    ruta_interna = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), script_a_abrir)

    if os.path.exists(ruta_interna):
        with open(ruta_interna, 'r', encoding='utf-8') as f:
            codigo = f.read()
        exec(codigo, {'__name__': '__main__', '__file__': ruta_interna})
    sys.exit(0)
# ─────────────────────────────────────────────────────────────

import customtkinter as ctk
from tkinter import messagebox

# Configuración estética global de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DashboardEstudios(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana principal
        self.title("Immune Study Suite 2026 - Dashboard")
        self.geometry("1200x680")
        self.resizable(False, False)

        # Matriz dinámica para registrar y matar los procesos hijos
        self.procesos_activos = []

        # Interfaz Gráfica (UI)
        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Frame Lateral Izquierdo (Menú)
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.lbl_logo = ctk.CTkLabel(
            self.sidebar,
            text="IMMUNE\nStudy Suite",
            font=("Segoe UI", 24, "bold"),
            text_color="#1f6aa5"
        )
        self.lbl_logo.pack(pady=(40, 30))

        # Indicador de Estado Cloud
        self.lbl_status = ctk.CTkLabel(
            self.sidebar,
            text="🟢 Servidores Groq Conectados",
            font=("Segoe UI", 12, "italic"),
            text_color="#2ecc71"
        )
        self.lbl_status.pack(pady=(0, 20))

        # Botones de navegación del Dashboard
        self.crear_boton_menu("📊 Calculador de Medias", "Calculador_Notas_Tkinter_FINAL.py")
        self.crear_boton_menu("📝 Apuntador de Notas", "Apuntador_Notas_Visual.py")
        self.crear_boton_menu("🔍 Resumidor de Textos AI", "resumidor_de_textos_visual.py")
        self.crear_boton_menu("🎯 Generador de Exámenes", "generador_examen_visual.py")
        self.crear_boton_menu("🤖 Ayudante de Problemas", "Ayudador_de_problemas_visual.py")
        self.crear_boton_menu("📅 Agenda de Estudios", "Calendario_FINAL.py")

        # Frame Central Derecho (Panel de Bienvenida)
        self.contenedor_principal = ctk.CTkFrame(self, corner_radius=15, fg_color="#1a1a1a")
        self.contenedor_principal.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.lbl_bienvenida = ctk.CTkLabel(
            self.contenedor_principal,
            text="¡Bienvenido a tu Suite de Estudios!",
            font=("Segoe UI", 28, "bold")
        )
        self.lbl_bienvenida.pack(pady=(150, 10))

        self.lbl_subtitulo = ctk.CTkLabel(
            self.contenedor_principal,
            text="Selecciona cualquier herramienta del menú lateral para empezar a trabajar.\nTodos los módulos de Inteligencia Artificial se ejecutan de forma optimizada en la nube.",
            font=("Segoe UI", 14),
            text_color="#888888"
        )
        self.lbl_subtitulo.pack(pady=10)

        # Manejo del cierre de ventana limpio
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar_ventana)

    def crear_boton_menu(self, texto, nombre_archivo):
        # Corregido: Eliminado 'padx' de los argumentos del botón
        btn = ctk.CTkButton(
            self.sidebar,
            text=texto,
            font=("Segoe UI", 14, "bold"),
            height=45,
            anchor="w",
            command=lambda: self.abrir_submodulo(nombre_archivo)
        )
        btn.pack(fill="x", padx=20, pady=8)

    def abrir_submodulo(self, nombre_archivo):
        try:
            if getattr(sys, 'frozen', False):
                # ENTORNO COMPILADO (EXE ÚNICO):
                exe_path = sys.executable
                env = os.environ.copy()
                if hasattr(sys, '_MEIPASS'):
                    env['_MEIPASS2'] = sys._MEIPASS

                proceso = subprocess.Popen([exe_path, nombre_archivo], env=env)
            else:
                # ENTORNO DE DESARROLLO LOCAL (uv):
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
    __spec__ = None  # Evita conflictos de contexto en algunos entornos con exec()
    app = DashboardEstudios()
    app.mainloop()