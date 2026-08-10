import sys
import os

# ─────────────────────────────────────────────────────────────────────────────
#  PARCHE INFACOBLES — BLINDAJE TOTAL PARA PYTHON 3.14 + DARKDETECT (macOS)
# ─────────────────────────────────────────────────────────────────────────────
class FakeDarkDetect:
    @staticmethod
    def isDark(): return True
    @staticmethod
    def isLight(): return False
    @staticmethod
    def theme(): return "Dark"

# Inyectamos el módulo falso directamente en la memoria antes de cualquier import
sys.modules['darkdetect'] = FakeDarkDetect
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
#  ENRUTADOR PYINSTALLER — macOS
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

# Configuración estética global de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DashboardEstudios(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ventana principal estilizada
        self.title("KernosssAI – Panel de Control")
        self.geometry("1240x720")
        self.resizable(False, False)
        self.configure(fg_color="#121214")  # Fondo oscuro premium ultra-clean

        self.procesos_activos = []
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar_ventana)

        self.configurar_interfaz()

    def configurar_interfaz(self):
        # ───── PANEL LATERAL IZQUIERDO (SIDEBAR) ─────
        self.sidebar = ctk.CTkFrame(
            self, 
            width=300, 
            corner_radius=0, 
            fg_color="#1a1a1e",  # Contraste sutil con el fondo
            border_color="#26262b",
            border_width=1
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Contenedor del título/logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(45, 40), padx=20, fill="x")

        lbl_logo_top = ctk.CTkLabel(
            logo_frame, 
            text="IMMUNE", 
            font=("SF Pro Display", 28, "bold"), 
            text_color="#3b82f6",  # Azul eléctrico vivo
            anchor="w"
        )
        lbl_logo_top.pack(fill="x")

        lbl_logo_sub = ctk.CTkLabel(
            logo_frame, 
            text="STUDY SUITE", 
            font=("SF Pro Text", 13, "bold"), 
            text_color="#64748b",  # Gris elegante apagado
            anchor="w"
        )
        lbl_logo_sub.pack(fill="x", pady=(2, 0))

        # Separador visual en el menú
        separador = ctk.CTkFrame(self.sidebar, height=2, fg_color="#26262b")
        separador.pack(fill="x", padx=20, pady=(0, 20))

        # Botones del Menú Lateral (Estilo Moderno de Pestañas)
        self.crear_boton_menu("📊  Calculadora de Medias", "Calculador_Notas_Tkinter_FINAL.py")
        self.crear_boton_menu("📝  Apuntador de Notas", "Apuntador_Notas_Visual.py")
        self.crear_boton_menu("🔍  Resumidor de Textos", "resumidor_de_textos_visual.py")
        self.crear_boton_menu("🎯  Generador de Exámenes", "generador_examen_visual.py")
        self.crear_boton_menu("🤖  Ayudador de Problemas", "Ayudador_de_problemas_visual.py")
        self.crear_boton_menu("📅  Agenda de Estudios", "Calendario_FINAL.py")

        # ───── PANEL PRINCIPAL DE BIENVENIDA (MAIN CONTENT) ─────
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=50, pady=50)

        lbl_bienvenida = ctk.CTkLabel(
            self.main_content, 
            text="¡Bienvenido a tu Espacio de Trabajo!", 
            font=("SF Pro Display", 32, "bold"),
            text_color="#f8fafc"
        )
        lbl_bienvenida.pack(anchor="w", pady=(0, 6))

        lbl_subtitulo = ctk.CTkLabel(
            self.main_content, 
            text="Optimiza tu rendimiento académico mediante herramientas avanzadas e Inteligencia Artificial.", 
            font=("SF Pro Text", 15),
            text_color="#94a3b8"
        )
        lbl_subtitulo.pack(anchor="w", pady=(0, 40))

        # Tarjeta informativa central minimalista (Card)
        info_card = ctk.CTkFrame(
            self.main_content, 
            corner_radius=20,
            fg_color="#1a1a1e",
            border_color="#26262b",
            border_width=1
        )
        info_card.pack(fill="both", expand=True)

        # Texto interior de la tarjeta formateado como bloque informativo limpio
        lbl_info_title = ctk.CTkLabel(
            info_card,
            text="Ecosistema Académico Unificado",
            font=("SF Pro Display", 22, "bold"),
            text_color="#3b82f6"
        )
        lbl_info_title.pack(pady=(40, 10))

        lbl_info_intro = ctk.CTkLabel(
            info_card,
            text="Esta suite unifica tus utilidades del día a día en un entorno de alto rendimiento.",
            font=("SF Pro Text", 15, "bold"),
            text_color="#cbd5e1"
        )
        lbl_info_intro.pack(pady=(0, 20))

        # Contenedor para simular un espaciado perfecto por filas de ítems
        items_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        items_frame.pack(fill="x", padx=60)

        item1 = ctk.CTkLabel(
            items_frame,
            text="•  Genera reportes formales automatizados en formato Word (.docx).",
            font=("SF Pro Text", 14),
            text_color="#94a3b8",
            anchor="w"
        )
        item1.pack(fill="x", pady=6)

        item2 = ctk.CTkLabel(
            items_frame,
            text="•  Resuelve problemas complejos mediante modelos inteligentes en la nube (Groq Cloud).",
            font=("SF Pro Text", 14),
            text_color="#94a3b8",
            anchor="w"
        )
        item2.pack(fill="x", pady=6)

        item3 = ctk.CTkLabel(
            items_frame,
            text="•  Gestor de agendas locales, calendarios y cálculos matemáticos sin salir de la app.",
            font=("SF Pro Text", 14),
            text_color="#94a3b8",
            anchor="w"
        )
        item3.pack(fill="x", pady=6)

    def crear_boton_menu(self, texto, nombre_archivo):
        btn = ctk.CTkButton(
            self.sidebar,
            text=texto,
            font=("SF Pro Text", 14, "bold"),
            height=46,
            anchor="w",
            corner_radius=10,
            fg_color="transparent",
            text_color="#94a3b8",
            hover_color="#26262b",
            command=lambda: self.abrir_submodulo(nombre_archivo)
        )
        btn.pack(fill="x", padx=16, pady=6)

    def abrir_submodulo(self, nombre_archivo):
        try:
            if getattr(sys, 'frozen', False):
                bundle_exe = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))),
                    "MacOS",
                    "KernosssAI"
                )
                exe_path = bundle_exe if os.path.isfile(bundle_exe) else sys.executable

                env = os.environ.copy()
                if hasattr(sys, '_MEIPASS'):
                    env['_MEIPASS2'] = sys._MEIPASS

                proceso = subprocess.Popen([exe_path, nombre_archivo], env=env)
            else:
                ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
                proceso = subprocess.Popen([sys.executable, ruta])

            self.procesos_activos.append(proceso)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el módulo:\n{e}")

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