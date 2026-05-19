import sys
import os

# ─────────────────────────────────────────────────────────────────────────────
#  ENRUTADOR PYINSTALLER — macOS
#  Cuando el .app lanza un subprocess pasándole el nombre del script como
#  argumento, este bloque intercepta la llamada y ejecuta ese módulo
#  directamente desde dentro del bundle, sin necesidad de carpetas externas.
# ─────────────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False) and len(sys.argv) > 1:
    script_a_abrir = sys.argv[1]
    ruta_interna = os.path.join(
        getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)),
        script_a_abrir
    )
    if os.path.exists(ruta_interna):
        with open(ruta_interna, 'r', encoding='utf-8') as f:
            codigo = f.read()
        exec(codigo, {'__name__': '__main__', '__file__': ruta_interna})
    sys.exit(0)
# ─────────────────────────────────────────────────────────────────────────────

import subprocess
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DashboardEstudios(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Immune Study Suite 2026")
        self.geometry("1200x680")
        self.resizable(False, False)

        self.procesos_activos = []
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar_ventana)

        self._construir_ui()

    # ──────────────────────────────────────────────────────────────────────────
    #  UI
    # ──────────────────────────────────────────────────────────────────────────
    def _construir_ui(self):
        # ── Sidebar izquierdo ──
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / nombre
        ctk.CTkLabel(
            self.sidebar,
            text="IMMUNE\nStudy Suite",
            font=("SF Pro Display", 24, "bold"),
            text_color="#1f6aa5",
            justify="center"
        ).pack(pady=(40, 6))

        # Indicador de estado de conexión cloud
        self.lbl_status = ctk.CTkLabel(
            self.sidebar,
            text="🟢 Groq Cloud conectado",
            font=("SF Pro Text", 11, "italic"),
            text_color="#2ecc71"
        )
        self.lbl_status.pack(pady=(0, 28))

        # Separador visual
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2d2d2d").pack(fill="x", padx=20, pady=(0, 20))

        # Botones de módulo
        modulos = [
            ("  📊  Calculadora de Medias",   "Calculador_Notas_Tkinter_FINAL.py"),
            ("  📝  Apuntador de Notas",       "Apuntador_Notas_Visual.py"),
            ("  🔍  Resumidor Académico IA",   "resumidor_de_textos_visual.py"),
            ("  🎯  Generador de Exámenes",    "generador_examen_visual.py"),
            ("  🤖  Ayudante de Problemas",    "Ayudador_de_problemas_visual.py"),
            ("  📅  Agenda y Calendario",      "Calendario_FINAL.py"),
        ]
        for texto, script in modulos:
            self._crear_boton(texto, script)

        # Separador y botón salir al fondo
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2d2d2d").pack(fill="x", padx=20, pady=(20, 16))

        ctk.CTkButton(
            self.sidebar,
            text="Cerrar suite",
            font=("SF Pro Text", 12),
            fg_color="#c62828",
            hover_color="#9e1c1c",
            height=38,
            corner_radius=8,
            command=self.al_cerrar_ventana
        ).pack(fill="x", padx=20, pady=(0, 20))

        # ── Panel derecho: bienvenida ──
        self.panel = ctk.CTkFrame(self, corner_radius=0, fg_color="#161616")
        self.panel.pack(side="right", fill="both", expand=True)

        # Contenedor centrado verticalmente
        centro = ctk.CTkFrame(self.panel, fg_color="transparent")
        centro.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(
            centro,
            text="Bienvenido a tu Suite de Estudios",
            font=("SF Pro Display", 26, "bold"),
            text_color="#f0f0f0"
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            centro,
            text="Selecciona una herramienta del menú lateral para empezar.",
            font=("SF Pro Text", 13),
            text_color="#666666"
        ).pack()

        ctk.CTkLabel(
            centro,
            text="Los módulos de IA se ejecutan en la nube — no requieren GPU local.",
            font=("SF Pro Text", 12),
            text_color="#444444"
        ).pack(pady=(4, 0))

        # Footer
        ctk.CTkLabel(
            self.panel,
            text="© 2026 Lander S.L & Immune Technology Institute",
            font=("SF Pro Text", 10),
            text_color="#333333"
        ).place(relx=0.5, rely=0.97, anchor="center")

    def _crear_boton(self, texto, script):
        ctk.CTkButton(
            self.sidebar,
            text=texto,
            font=("SF Pro Text", 13, "bold"),
            height=44,
            anchor="w",
            fg_color="transparent",
            hover_color="#1e1e1e",
            text_color=["#1a1a1a", "#e0e0e0"],
            border_width=0,
            corner_radius=8,
            command=lambda s=script: self._lanzar(s)
        ).pack(fill="x", padx=16, pady=4)

    # ──────────────────────────────────────────────────────────────────────────
    #  Lanzador de submódulos
    # ──────────────────────────────────────────────────────────────────────────
    def _lanzar(self, nombre_archivo):
        try:
            if getattr(sys, 'frozen', False):
                # Dentro del .app: localizar el binario ejecutable real
                bundle_exe = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))),
                    "MacOS",
                    "Immune Study Suite"
                )
                exe_path = bundle_exe if os.path.isfile(bundle_exe) else sys.executable

                env = os.environ.copy()
                if hasattr(sys, '_MEIPASS'):
                    env['_MEIPASS2'] = sys._MEIPASS

                proceso = subprocess.Popen([exe_path, nombre_archivo], env=env)
            else:
                # Desarrollo local
                ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
                proceso = subprocess.Popen([sys.executable, ruta])

            self.procesos_activos.append(proceso)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo:\n{e}")

    # ──────────────────────────────────────────────────────────────────────────
    #  Cierre limpio
    # ──────────────────────────────────────────────────────────────────────────
    def al_cerrar_ventana(self):
        for p in self.procesos_activos:
            if p.poll() is None:
                try:
                    p.kill()
                except Exception:
                    pass
        self.quit()
        self.destroy()
        os._exit(0)


if __name__ == "__main__":
    __spec__ = None
    app = DashboardEstudios()
    app.mainloop()
