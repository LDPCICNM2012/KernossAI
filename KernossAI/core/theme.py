"""
KernossAI - Sistema de Diseño y Tokens de Color
Constantes visuales, paleta de colores, tipografías y utilidades de ventana.
"""

import os
import re
import sys
import customtkinter as ctk

VERSION_APP = "1.8.0"

# ─────────────────────────────────────────────────────────────
#  PALETA DE COLORES Y TOKENS VISUALES (MODO BLANCO / MODO OSCURO)
#  Formato CustomTkinter: (Color Modo Blanco, Color Modo Oscuro)
# ─────────────────────────────────────────────────────────────
COLOR_BG_DARK       = ("#f8fafc", "#050811")  # Fondo base de la ventana
COLOR_BG_SIDEBAR    = ("#f1f5f9", "#070c18")  # Fondo sidebar lateral
COLOR_BG_CARD       = ("#ffffff", "#0a1124")  # Paneles y tarjetas base
COLOR_BG_CARD_LIGHT = ("#ffffff", "#0f1a35")  # Entradas de texto y visores
COLOR_BG_SURFACE    = ("#e2e8f0", "#152449")  # Superficies activas
COLOR_BORDER        = ("#cbd5e1", "#1e3a6a")  # Bordes sutiles
COLOR_BORDER_GLOW   = ("#2563eb", "#3b82f6")  # Borde con resplandor activo

COLOR_ACCENT_PRIMARY      = ("#2563eb", "#2563eb") # Azul Eléctrico principal
COLOR_ACCENT_HOVER        = ("#1d4ed8", "#3b82f6") # Azul hover brillante
COLOR_ACCENT_CYAN         = ("#0284c7", "#06b6d4") # Cian brillante
COLOR_ACCENT_CYAN_HOVER   = ("#0369a1", "#0891b2")
COLOR_ACCENT_SKY          = ("#0284c7", "#38bdf8") # Celeste
COLOR_ACCENT_PURPLE       = ("#6366f1", "#6366f1") # Indigo (Docentes)
COLOR_ACCENT_PURPLE_HOVER = ("#4f46e5", "#4f46e5")

COLOR_TEXT_MAIN      = ("#0f172a", "#f8fafc") # Texto principal (Negro en modo blanco, Blanco en modo oscuro)
COLOR_TEXT_MUTED     = ("#475569", "#94a3b8") # Gris secundario
COLOR_TEXT_DIM       = ("#94a3b8", "#64748b") # Gris tenue / placeholder
COLOR_SUCCESS        = ("#16a34a", "#10b981") # Verde esmeralda
COLOR_SUCCESS_HOVER  = ("#15803d", "#059669")
COLOR_WARNING        = ("#d97706", "#f59e0b") # Ámbar
COLOR_DANGER         = ("#dc2626", "#ef4444") # Rojo coral
COLOR_DANGER_HOVER   = ("#b91c1c", "#dc2626")

# ─────────────────────────────────────────────────────────────
#  UTILIDADES DE VENTANA Y HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
_PATCHES_APLICADOS = False

def configurar_defaults_ctk():
    """Garantiza que ningún componente de CustomTkinter muestre texto blanco en modo blanco."""
    global _PATCHES_APLICADOS
    try:
        ctk.ThemeManager.theme["CTkButton"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkSegmentedButton"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkOptionMenu"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkLabel"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkEntry"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkTextbox"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkComboBox"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkCheckBox"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkRadioButton"]["text_color"] = ["#0f172a", "#f8fafc"]
        ctk.ThemeManager.theme["CTkSwitch"]["text_color"] = ["#0f172a", "#f8fafc"]
        if "DropdownMenu" in ctk.ThemeManager.theme:
            ctk.ThemeManager.theme["DropdownMenu"]["text_color"] = ["#0f172a", "#f8fafc"]
            ctk.ThemeManager.theme["DropdownMenu"]["fg_color"] = ["#ffffff", "#0a1124"]
            ctk.ThemeManager.theme["DropdownMenu"]["hover_color"] = ["#e2e8f0", "#152449"]
    except Exception:
        pass

    if _PATCHES_APLICADOS:
        return
    _PATCHES_APLICADOS = True

    try:
        # 1. Auto-contraste de CTkButton según su color de fondo
        _orig_btn_init = ctk.CTkButton.__init__
        def _patched_btn_init(self, master, *args, **kwargs):
            if "text_color" not in kwargs or kwargs.get("text_color") is None:
                fg = kwargs.get("fg_color")
                dark_accents = [
                    "#2563eb", "#1d4ed8", "#10b981", "#15803d", "#16a34a", "#059669",
                    "#ef4444", "#dc2626", "#b91c1c", "#7f1d1d", "#991b1b",
                    "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81", "#1e1b4b",
                    "#0284c7", "#0369a1", "#06b6d4", "#0891b2", "#064e3b", "#0c2d48", "#0c234a"
                ]
                is_dark_accent = False
                if isinstance(fg, str) and any(fg.lower().startswith(a.lower()) for a in dark_accents):
                    is_dark_accent = True
                elif isinstance(fg, (tuple, list)) and any(isinstance(c, str) and any(c.lower().startswith(a.lower()) for a in dark_accents) for c in fg):
                    is_dark_accent = True
                kwargs["text_color"] = "#ffffff" if is_dark_accent else COLOR_TEXT_MAIN
            _orig_btn_init(self, master, *args, **kwargs)
        ctk.CTkButton.__init__ = _patched_btn_init

        # 2. Pestaña activa blanca y pestañas inactivas oscuras en CTkSegmentedButton
        _orig_seg_select = ctk.CTkSegmentedButton._select_button_by_value
        _orig_seg_unselect = ctk.CTkSegmentedButton._unselect_button_by_value
        def _patched_seg_select(self, value):
            _orig_seg_select(self, value)
            if hasattr(self, "_buttons_dict") and value in self._buttons_dict:
                self._buttons_dict[value].configure(text_color="#ffffff")
        def _patched_seg_unselect(self, value):
            _orig_seg_unselect(self, value)
            if hasattr(self, "_buttons_dict") and value in self._buttons_dict:
                self._buttons_dict[value].configure(text_color=self._sb_text_color if hasattr(self, "_sb_text_color") and self._sb_text_color else COLOR_TEXT_MAIN)
        ctk.CTkSegmentedButton._select_button_by_value = _patched_seg_select
        ctk.CTkSegmentedButton._unselect_button_by_value = _patched_seg_unselect

        # 3. CTkOptionMenu
        _orig_opt_init = ctk.CTkOptionMenu.__init__
        def _patched_opt_init(self, master, *args, **kwargs):
            if "text_color" not in kwargs or kwargs.get("text_color") is None:
                fg = kwargs.get("fg_color")
                if fg in ("#2563eb", COLOR_ACCENT_PRIMARY):
                    kwargs["text_color"] = "#ffffff"
                else:
                    kwargs["text_color"] = COLOR_TEXT_MAIN
            if "dropdown_text_color" not in kwargs or kwargs.get("dropdown_text_color") is None:
                kwargs["dropdown_text_color"] = COLOR_TEXT_MAIN
            if "dropdown_fg_color" not in kwargs or kwargs.get("dropdown_fg_color") is None:
                kwargs["dropdown_fg_color"] = COLOR_BG_CARD
            _orig_opt_init(self, master, *args, **kwargs)
        ctk.CTkOptionMenu.__init__ = _patched_opt_init

        # 4. CTkEntry (texto negro al escribir en modo blanco, blanco en modo oscuro)
        _orig_entry_init = ctk.CTkEntry.__init__
        def _patched_entry_init(self, master, *args, **kwargs):
            if "text_color" not in kwargs or kwargs.get("text_color") is None:
                kwargs["text_color"] = COLOR_TEXT_MAIN
            if "placeholder_text_color" not in kwargs or kwargs.get("placeholder_text_color") is None:
                kwargs["placeholder_text_color"] = COLOR_TEXT_DIM
            _orig_entry_init(self, master, *args, **kwargs)
        ctk.CTkEntry.__init__ = _patched_entry_init

        # 5. CTkTextbox (texto negro en visores y entradas en modo blanco)
        _orig_txt_init = ctk.CTkTextbox.__init__
        def _patched_txt_init(self, master, *args, **kwargs):
            if "text_color" not in kwargs or kwargs.get("text_color") is None:
                kwargs["text_color"] = COLOR_TEXT_MAIN
            _orig_txt_init(self, master, *args, **kwargs)
        ctk.CTkTextbox.__init__ = _patched_txt_init
    except Exception:
        pass

configurar_defaults_ctk()

def aplicar_tema(tema: str = None):
    """
    Aplica el modo visual a nivel global en CustomTkinter:
    'dark' / 'oscuro': Modo Oscuro (fondo negro, texto blanco)
    'light' / 'blanco': Modo Blanco (fondo blanco, texto negro)
    """
    configurar_defaults_ctk()
    if tema is None:
        try:
            from KernossAI.core.config import obtener_tema
            tema = obtener_tema()
        except Exception:
            tema = "dark"
    if str(tema).lower() in ("light", "blanco", "claro"):
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")


def aplicar_icono(ventana):
    """Aplica el icono institucional según la plataforma (Windows .ico, macOS .icns)."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ico_path = os.path.join(base_dir, "logo.ico")
        if sys.platform == "win32" and os.path.exists(ico_path):
            ventana.iconbitmap(ico_path)
    except Exception:
        pass


def centrar_ventana(ventana, ancho: int, alto: int):
    """Centra una ventana en la pantalla del usuario considerando escalado de DPI."""
    ventana.update_idletasks()
    sw = ventana.winfo_screenwidth()
    sh = ventana.winfo_screenheight()
    x = max(0, (sw - ancho) // 2)
    y = max(0, (sh - alto) // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def es_version_superior(remota: str, local: str) -> bool:
    """Compara si la versión remota (ej: 'v1.6') es superior a la local (ej: '1.5')."""
    try:
        def parse_nums(v):
            return [int(x) for x in re.findall(r'\d+', str(v))]
        v_remota = parse_nums(remota)
        v_local = parse_nums(local)
        return v_remota > v_local
    except Exception:
        return remota.lstrip('vV').strip() != local.lstrip('vV').strip()


def construir_prompt(instrucciones: str, historial: list = None) -> str:
    """Construye un prompt de chat unificado a partir de un historial y un system prompt."""
    partes = [instrucciones.strip()]
    if historial:
        for msg in historial:
            rol = "IA" if msg.get("role") == "assistant" else msg.get("role", "Usuario").capitalize()
            partes.append(f"{rol}: {msg.get('content', '')}")
    return "\n\n".join(partes)
