"""
KernossAI - Sistema de Diseño y Tokens de Color
Constantes visuales, paleta de colores, tipografías y utilidades de ventana.
"""

import os
import re
import sys
import customtkinter as ctk

VERSION_APP = "1.6"

# ─────────────────────────────────────────────────────────────
#  PALETA DE COLORES Y TOKENS VISUALES
# ─────────────────────────────────────────────────────────────
COLOR_BG_DARK       = "#050811"  # Fondo base de la ventana
COLOR_BG_SIDEBAR    = "#070c18"  # Fondo sidebar lateral
COLOR_BG_CARD       = "#0a1124"  # Paneles y tarjetas base
COLOR_BG_CARD_LIGHT = "#0f1a35"  # Entradas de texto y visores
COLOR_BG_SURFACE    = "#152449"  # Superficies activas
COLOR_BORDER        = "#1e3a6a"  # Bordes azulados sutiles
COLOR_BORDER_GLOW   = "#3b82f6"  # Borde con resplandor activo

COLOR_ACCENT_PRIMARY      = "#2563eb" # Azul Eléctrico principal
COLOR_ACCENT_HOVER        = "#3b82f6" # Azul hover brillante
COLOR_ACCENT_CYAN         = "#06b6d4" # Cian brillante
COLOR_ACCENT_CYAN_HOVER   = "#0891b2"
COLOR_ACCENT_SKY          = "#38bdf8" # Celeste
COLOR_ACCENT_PURPLE       = "#6366f1" # Indigo (Docentes)
COLOR_ACCENT_PURPLE_HOVER = "#4f46e5"

COLOR_TEXT_MAIN      = "#f8fafc" # Blanco nítido
COLOR_TEXT_MUTED     = "#94a3b8" # Gris azulado secundario
COLOR_TEXT_DIM       = "#64748b" # Gris tenue
COLOR_SUCCESS        = "#10b981" # Verde esmeralda
COLOR_SUCCESS_HOVER  = "#059669"
COLOR_WARNING        = "#f59e0b" # Ámbar
COLOR_DANGER         = "#ef4444" # Rojo coral
COLOR_DANGER_HOVER   = "#dc2626"

# ─────────────────────────────────────────────────────────────
#  UTILIDADES DE VENTANA Y HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
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
