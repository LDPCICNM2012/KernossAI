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
def aplicar_tema(tema: str = None):
    """
    Aplica el modo visual a nivel global en CustomTkinter:
    'dark' / 'oscuro': Modo Oscuro (fondo negro, texto blanco)
    'light' / 'blanco': Modo Blanco (fondo blanco, texto negro)
    """
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
