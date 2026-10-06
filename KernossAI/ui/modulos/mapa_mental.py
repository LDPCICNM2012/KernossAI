"""
KernossAI - Módulo: Mapas Mentales y Conceptuales Avanzados con IA
Generador de diagramas conceptuales profundos con tarjetas informativas,
soporte para análisis visual multimodal de imágenes (apuntes, fotos de libros, diapositivas),
visualizador HD interactivo con Zoom/Pan, modo Fichas de Estudio y exportación.
"""

import os
import re
import json
import textwrap
import threading
from datetime import datetime
import numpy as np
import customtkinter as ctk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from KernossAI.core.theme import (
    COLOR_BG_CARD,
    COLOR_BG_CARD_LIGHT,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_CYAN_HOVER,
    COLOR_ACCENT_SKY,
    COLOR_ACCENT_PURPLE,
    COLOR_ACCENT_PURPLE_HOVER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_SUCCESS,
    COLOR_SUCCESS_HOVER,
    COLOR_DANGER,
)
from KernossAI.core.i18n import t
from KernossAI.core.auth import llamar_groq, llamar_gemini, consultar_ia_multimodal

INSTRUCCIONES_MAPA_MENTAL = """
Eres un pedagogo y científico experto en síntesis visual avanzada, mapas conceptuales educativos de alto nivel y pensamiento sistémico.
Tu objetivo es transformar el tema académico solicitado o el contenido de las imágenes adjuntas en un Mapa Conceptual/Mental PROFUNDO, EXHAUSTIVO, RICO EN INFORMACIÓN Y ALTAMENTE ESTRUCTURADO (similar a los esquemas infográficos universitarios).

REGLAS OBLIGATORIAS:
1. NO te limites a palabras sueltas ni esquemas vacíos. Cada rama y subtema DEBE DESARROLLARSE CON INFORMACIÓN REAL, científica, histórica o técnica.
2. Genera entre 6 y 8 EJES O RAMAS PRINCIPALES que cubran todas las dimensiones del tema:
   - Origen, Historia y Descubrimientos clave (con nombres de científicos, fechas, teorías).
   - Fundamentos, Principios o Postulados esenciales.
   - Clasificación, Tipos o Taxonomías (con comparativas y características distintivas).
   - Estructura, Mecanismos, Fisiología o Funcionamiento interno.
   - Propiedades, Leyes, Procesos Metabólicos/Técnicos o Funciones.
   - Aplicaciones Prácticas, Terapias, Casos de Estudio o Ejemplos Reales.
   - Métricas, Escalas, Unidades de Medida o Límites Físicos.
   - Agentes Relacionados, Excepciones, Desafíos o Futuro.
3. Para CADA rama principal, genera de 2 a 4 SUB-RAMAS (subtemas).
4. Para CADA sub-rama, proporciona:
   - "titulo": Nombre del subtema concreto.
   - "puntos_detalle": Lista de 2 a 5 puntos explicativos ricos (oraciones completas, datos numéricos, mecanismos, leyes o definiciones claras).
   - "conceptos_clave": Lista de 2 a 4 palabras clave o términos destacados.

Debes responder ÚNICAMENTE con un objeto JSON válido (sin texto antes ni después, sin bloques ```think```):
{
  "tema_central": "Título conciso del tema central",
  "descripcion_general": "Resumen conceptual claro y riguroso de 2 o 3 líneas sobre la definición fundamental del tema.",
  "ramas": [
    {
      "titulo": "ORIGEN & HISTORIA",
      "color": "#a855f7",
      "descripcion": "Antecedentes históricos y teorías fundamentales.",
      "sub_ramas": [
        {
          "titulo": "Descubrimiento y Primeras Observaciones",
          "puntos_detalle": [
            "Robert Hooke (1665) observó celdillas en corcho mediante microscopio y acuñó el término.",
            "Antonie van Leeuwenhoek descubrió microorganismos vivos ('animálculos') en gotas de agua."
          ],
          "conceptos_clave": ["Robert Hooke", "Leeuwenhoek", "Microscopía"]
        },
        {
          "titulo": "Teoría Celular Clásica",
          "puntos_detalle": [
            "Propuesta por Schleiden, Schwann y Virchow.",
            "1. Unidad estructural: Todos los seres vivos están integrados por células.",
            "2. Unidad de origen: Toda célula proviene de otra preexistente (Omnis cellula e cellula)."
          ],
          "conceptos_clave": ["Schleiden & Schwann", "Virchow", "Omnis cellula"]
        }
      ]
    }
  ]
}
"""


class MindMapRenderer:
    """Motor de cálculo geométrico y renderizado gráfico HD para mapas conceptuales."""
    PALETA_DEFAULT = [
        "#a855f7",  # Violeta
        "#f97316",  # Naranja
        "#10b981",  # Verde Esmeralda
        "#ef4444",  # Rojo Coral
        "#06b6d4",  # Cian
        "#eab308",  # Ámbar / Oro
        "#8b5cf6",  # Púrpura Real
        "#ec4899",  # Rosa
        "#14b8a6",  # Turquesa
    ]

    @staticmethod
    def calculate_card_lines(sub, max_width=38):
        sub_title = sub.get("titulo") or sub.get("nombre") or "Subtema"
        sub_title = sub_title.strip()
        puntos = sub.get("puntos_detalle") or sub.get("puntos") or []
        if isinstance(puntos, str):
            puntos = [puntos]

        detalle = sub.get("detalle")
        if detalle and not puntos:
            puntos = [detalle]

        conceptos = sub.get("conceptos_clave") or sub.get("claves") or []
        if isinstance(conceptos, str):
            conceptos = [c.strip() for c in conceptos.split(",")]

        lines = [f">> {sub_title.upper()}"]
        lines.append("-" * min(max_width, max(len(sub_title) + 6, 22)))

        for p in puntos:
            p_clean = str(p).strip()
            if not p_clean.startswith("•") and not p_clean.startswith("*") and not p_clean.startswith("-"):
                p_clean = f"• {p_clean}"
            wrapped = textwrap.fill(p_clean, width=max_width)
            lines.extend(wrapped.split("\n"))

        if conceptos:
            claves_str = ", ".join(conceptos)
            wrapped_c = textwrap.fill(f"Claves: {claves_str}", width=max_width)
            lines.append("")
            lines.extend(wrapped_c.split("\n"))

        return lines

    @classmethod
    def render(cls, ax, datos):
        ax.clear()
        ax.set_facecolor("#060913")

        tema_central = datos.get("tema_central", "Tema Central")
        ramas = datos.get("ramas", [])
        num_ramas = len(ramas)

        if num_ramas == 0:
            ax.text(0, 0, "🧠 Escribe un tema o adjunta imágenes de apuntes\ny haz clic en 'Generar Mapa' para crear el esquema",
                    color="#94a3b8", fontsize=11, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.8", facecolor="#0c1427", edgecolor="#1e3a6a", lw=1.5))
            ax.set_xlim(-10, 10)
            ax.set_ylim(-10, 10)
            ax.axis("off")
            return (-10, 10, -10, 10)

        num_right = (num_ramas + 1) // 2
        right_ramas = ramas[:num_right]
        left_ramas = ramas[num_right:]

        LINE_HEIGHT_UNITS = 0.33
        CARD_PADDING_Y = 0.90
        GAP_BETWEEN_CARDS = 0.75

        def layout_side_cards(side_ramas, is_right=True):
            side_items = []
            for i, rama in enumerate(side_ramas):
                color_idx = i if is_right else (i + num_right)
                color = rama.get("color") or cls.PALETA_DEFAULT[color_idx % len(cls.PALETA_DEFAULT)]
                titulo_rama = rama.get("titulo", f"Rama {i+1}")
                sub_ramas = rama.get("sub_ramas") or rama.get("sub_conceptos") or []

                rama_card_objs = []
                for j, sub in enumerate(sub_ramas):
                    lines = cls.calculate_card_lines(sub, max_width=38)
                    h_units = (len(lines) * LINE_HEIGHT_UNITS) + CARD_PADDING_Y
                    rama_card_objs.append({
                        "sub_data": sub,
                        "lines": lines,
                        "height": h_units,
                        "color": color,
                        "branch_title": titulo_rama
                    })

                if not rama_card_objs:
                    desc = rama.get("descripcion", "Detalles conceptuales del tema.")
                    wrapped = textwrap.fill(f"• {desc}", width=38).split("\n")
                    lines = [f">> {titulo_rama.upper()}", "-" * 24] + wrapped
                    h_units = (len(lines) * LINE_HEIGHT_UNITS) + CARD_PADDING_Y
                    rama_card_objs.append({
                        "sub_data": {},
                        "lines": lines,
                        "height": h_units,
                        "color": color,
                        "branch_title": titulo_rama
                    })

                side_items.append({
                    "rama_title": titulo_rama,
                    "color": color,
                    "cards": rama_card_objs
                })
            return side_items

        right_items = layout_side_cards(right_ramas, is_right=True)
        left_items = layout_side_cards(left_ramas, is_right=False)

        def position_items(items):
            total_height = sum(sum(c["height"] for c in it["cards"]) + (len(it["cards"]) - 1) * GAP_BETWEEN_CARDS for it in items)
            total_height += (len(items) - 1) * (GAP_BETWEEN_CARDS * 1.4)

            cur_y = total_height / 2.0
            for it in items:
                cat_card_y_list = []
                for c in it["cards"]:
                    card_center_y = cur_y - (c["height"] / 2.0)
                    c["y"] = card_center_y
                    cat_card_y_list.append(card_center_y)
                    cur_y -= (c["height"] + GAP_BETWEEN_CARDS)
                it["cat_y"] = np.mean(cat_card_y_list) if cat_card_y_list else 0
                cur_y -= (GAP_BETWEEN_CARDS * 0.5)
            return total_height

        h_right = position_items(right_items)
        h_left = position_items(left_items)
        max_h = max(h_right, h_left, 14.0)

        X_CENTER_OFFSET = 4.2
        X_CARD_OFFSET = 9.3

        # Dibujar Nodo Central
        desc_gen = datos.get("descripcion_general", "")
        if desc_gen:
            w_desc = textwrap.fill(desc_gen, width=34)
            full_center_text = f"{tema_central.upper()}\n{'─'*26}\n{w_desc}"
        else:
            full_center_text = f"{tema_central.upper()}"

        ax.text(0, 0, full_center_text,
                color="#ffffff", fontsize=10.5, fontweight="bold", ha="center", va="center", linespacing=1.32,
                bbox=dict(boxstyle="round,pad=1.0,rounding_size=0.6", facecolor="#1e3a8a", edgecolor="#38bdf8", lw=3.0, alpha=0.98))

        def render_placed_side(items, is_right=True):
            sign = 1 if is_right else -1

            for it in items:
                cat_x = sign * X_CENTER_OFFSET
                cat_y = it["cat_y"]
                color = it["color"]
                title = it["rama_title"]

                # Curva Bezier desde Centro (0, 0) a Categoría
                c1_x = sign * (X_CENTER_OFFSET * 0.45)
                c1_y = 0
                c2_x = sign * (X_CENTER_OFFSET * 0.65)
                c2_y = cat_y
                end_x = cat_x - (sign * 0.9)

                verts = [(0, 0), (c1_x, c1_y), (c2_x, c2_y), (end_x, cat_y)]
                codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                path = Path(verts, codes)
                ax.add_patch(PathPatch(path, facecolor='none', edgecolor=color, lw=3.2, alpha=0.9, capstyle='round'))

                # Placa de Categoría
                ax.text(cat_x, cat_y, f"  {title.upper()}  ",
                        color="#ffffff", fontsize=10, fontweight="bold", ha="center", va="center",
                        bbox=dict(boxstyle="round,pad=0.55,rounding_size=0.35", facecolor="#0e172a", edgecolor=color, lw=2.4, alpha=0.98))

                # Tarjetas de Subtemas
                for c in it["cards"]:
                    card_y = c["y"]
                    card_x = sign * X_CARD_OFFSET

                    bc1_x = cat_x + (sign * 1.5)
                    bc1_y = cat_y
                    bc2_x = card_x - (sign * 1.5)
                    bc2_y = card_y
                    c_start_x = cat_x + (sign * 0.9)
                    c_end_x = card_x - (sign * 0.2)

                    sub_verts = [(c_start_x, cat_y), (bc1_x, bc1_y), (bc2_x, bc2_y), (c_end_x, card_y)]
                    sub_codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                    sub_path = Path(sub_verts, sub_codes)
                    ax.add_patch(PathPatch(sub_path, facecolor='none', edgecolor=color, lw=1.8, ls="--", alpha=0.75))

                    text_content = "\n".join(c["lines"])
                    ax.text(card_x, card_y, text_content,
                            color="#f1f5f9", fontsize=8.2, ha="left" if is_right else "right", va="center", linespacing=1.28,
                            bbox=dict(boxstyle="round,pad=0.6,rounding_size=0.2", facecolor="#091122", edgecolor=color, lw=1.5, alpha=0.96))

        render_placed_side(right_items, is_right=True)
        render_placed_side(left_items, is_right=False)

        y_limit = (max_h / 2.0) + 1.8
        x_limit = X_CARD_OFFSET + 7.8
        ax.set_xlim(-x_limit, x_limit)
        ax.set_ylim(-y_limit, y_limit)
        ax.axis("off")
        return (-x_limit, x_limit, -y_limit, y_limit)


class ModuloMapaMental(ctk.CTkFrame):
    """Módulo interactivo de mapas mentales con editor JSON, visualización gráfica interactiva y exportación."""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.modelo_actual = "gemini"
        self.datos_mapa = None
        self.fig = None
        self.ax = None
        self.canvas_grafico = None
        self.imagenes_adjuntas = []
        
        # Estado de navegación Pan & Zoom
        self._orig_limits = (-15, 15, -12, 12)
        self._panning = False
        self._pan_start = (0, 0)
        self._pan_start_limits = None
        
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=4, minsize=430)
        self.grid_columnconfigure(1, weight=7, minsize=600)
        self.grid_rowconfigure(0, weight=1)

        # ── PANEL IZQUIERDO: CONTROLES & CONFIGURACIÓN ──
        panel_izq = ctk.CTkFrame(self, corner_radius=14, fg_color=COLOR_BG_CARD,
                                 border_width=1, border_color=COLOR_BORDER)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        panel_izq.grid_rowconfigure(8, weight=1)
        panel_izq.grid_columnconfigure(0, weight=1)

        frame_header = ctk.CTkFrame(panel_izq, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))

        ctk.CTkLabel(frame_header, text=t("mapa_titulo"),
                     font=("Segoe UI", 18, "bold"), text_color=COLOR_ACCENT_SKY).pack(anchor="w")
        ctk.CTkLabel(frame_header, text="Genera esquemas conceptuales a partir de temas o imágenes de apuntes.",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        # Input de Tema
        ctk.CTkLabel(panel_izq, text=t("mapa_lbl_tema"),
                     font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).grid(row=1, column=0, sticky="w", padx=18, pady=(4, 2))
        self.entry_tema = ctk.CTkEntry(
            panel_izq, placeholder_text="Ej: La Célula (o deja vacío si subes imágenes)",
            height=36, font=("Segoe UI", 12),
            fg_color=COLOR_BG_CARD_LIGHT, text_color=COLOR_TEXT_MAIN,
            placeholder_text_color=COLOR_TEXT_DIM, border_color=COLOR_BORDER
        )
        self.entry_tema.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 8))
        self.entry_tema.bind("<Return>", lambda e: self.generar_mapa_mental())

        # Opciones de Nivel y Enfoque
        frame_opts = ctk.CTkFrame(panel_izq, fg_color="transparent")
        frame_opts.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 8))
        frame_opts.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame_opts, text="Nivel / Audiencia:", font=("Segoe UI", 11, "bold"),
                     text_color=COLOR_TEXT_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 2))
        self.combo_nivel = ctk.CTkComboBox(frame_opts,
                                           values=["Universidad / Avanzado", "Bachillerato / High School", "Secundaria / ESO", "Primaria", "General / Divulgativo"],
                                           font=("Segoe UI", 11), height=32,
                                           fg_color=COLOR_BG_CARD_LIGHT, border_color=COLOR_BORDER)
        self.combo_nivel.set("Universidad / Avanzado")
        self.combo_nivel.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(frame_opts, text="Enfoque Opcional:", font=("Segoe UI", 11, "bold"),
                     text_color=COLOR_TEXT_MUTED).grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 2))
        self.entry_enfoque = ctk.CTkEntry(
            frame_opts, placeholder_text="Puntos clave...",
            font=("Segoe UI", 11), height=32,
            fg_color=COLOR_BG_CARD_LIGHT, text_color=COLOR_TEXT_MAIN,
            placeholder_text_color=COLOR_TEXT_DIM, border_color=COLOR_BORDER
        )
        self.entry_enfoque.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # ── SECCIÓN DE SUBIDA MULTIMODAL DE IMÁGENES ──
        frame_img_box = ctk.CTkFrame(panel_izq, fg_color=COLOR_BG_CARD_LIGHT, corner_radius=10,
                                     border_width=1, border_color=COLOR_BORDER)
        frame_img_box.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 8))

        f_img_top = ctk.CTkFrame(frame_img_box, fg_color="transparent")
        f_img_top.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(f_img_top, text="📷 Extraer de Imágenes (Apuntes/Libros):",
                     font=("Segoe UI", 11, "bold"), text_color=COLOR_ACCENT_CYAN).pack(side="left")

        self.lbl_img_count = ctk.CTkLabel(f_img_top, text="0 fotos", font=("Segoe UI", 10),
                                          text_color=COLOR_TEXT_MUTED)
        self.lbl_img_count.pack(side="right")

        f_img_btns = ctk.CTkFrame(frame_img_box, fg_color="transparent")
        f_img_btns.pack(fill="x", padx=10, pady=(0, 6))

        self.btn_adjuntar_img = ctk.CTkButton(f_img_btns, text="📁 Subir Varias Imágenes", height=28,
                                              font=("Segoe UI", 11, "bold"),
                                              fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                                              border_width=1, border_color=COLOR_BORDER,
                                              command=self._adjuntar_imagenes)
        self.btn_adjuntar_img.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_limpiar_img = ctk.CTkButton(f_img_btns, text="🗑️", width=34, height=28,
                                             font=("Segoe UI", 11),
                                             fg_color=COLOR_BG_SURFACE, hover_color=COLOR_DANGER,
                                             border_width=1, border_color=COLOR_BORDER,
                                             command=self._limpiar_imagenes)
        self.btn_limpiar_img.pack(side="right")

        # Scroll / Chips de imágenes adjuntas
        self.scroll_img_chips = ctk.CTkScrollableFrame(frame_img_box, fg_color="transparent", height=42, orientation="horizontal")
        self.scroll_img_chips.pack(fill="x", padx=8, pady=(0, 6))
        self._actualizar_chips_imagenes()

        # Selector de Modelo y Botón de Generar
        frame_ia_bar = ctk.CTkFrame(panel_izq, fg_color="transparent")
        frame_ia_bar.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 6))
        frame_ia_bar.grid_columnconfigure(1, weight=1)

        frame_model_switch = ctk.CTkFrame(frame_ia_bar, fg_color=COLOR_BG_CARD_LIGHT,
                                          border_width=1, border_color=COLOR_BORDER, corner_radius=8)
        frame_model_switch.grid(row=0, column=0, sticky="w")

        self.btn_gemini = ctk.CTkButton(frame_model_switch, text="🧠 Gemini (Visión)", height=28, width=100,
                                        font=("Segoe UI", 10, "bold"),
                                        fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                                        command=lambda: self._set_modelo("gemini"))
        self.btn_gemini.pack(side="left", padx=2, pady=2)

        self.btn_groq = ctk.CTkButton(frame_model_switch, text="⚡ Groq", height=28, width=70,
                                      font=("Segoe UI", 10, "bold"),
                                      fg_color="transparent", hover_color=COLOR_ACCENT_PURPLE_HOVER,
                                      command=lambda: self._set_modelo("groq"))
        self.btn_groq.pack(side="left", padx=2, pady=2)

        self.btn_generar = ctk.CTkButton(frame_ia_bar, text="🧠 Generar Mapa Conceptual", height=36,
                                         font=("Segoe UI", 12, "bold"),
                                         fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                                         command=self.generar_mapa_mental)
        self.btn_generar.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        self.lbl_status = ctk.CTkLabel(panel_izq, text="Listo para procesar", font=("Segoe UI", 11),
                                       text_color=COLOR_TEXT_DIM)
        self.lbl_status.grid(row=6, column=0, sticky="w", padx=18, pady=(0, 4))

        # Panel de Temas Sugeridos
        frame_quick = ctk.CTkFrame(panel_izq, fg_color=COLOR_BG_CARD_LIGHT, corner_radius=10,
                                   border_width=1, border_color=COLOR_BORDER)
        frame_quick.grid(row=7, column=0, sticky="ew", padx=18, pady=(0, 8))
        
        ctk.CTkLabel(frame_quick, text="💡 Sugerencias Rápidas:", font=("Segoe UI", 10, "bold"),
                     text_color=COLOR_ACCENT_CYAN).pack(anchor="w", padx=10, pady=(4, 2))
        
        frame_tags = ctk.CTkFrame(frame_quick, fg_color="transparent")
        frame_tags.pack(fill="x", padx=6, pady=(0, 4))
        
        sugerencias = ["La Célula", "Fotosíntesis", "Redes Neuronales", "Revolución Industrial"]
        for sug in sugerencias:
            b_tag = ctk.CTkButton(frame_tags, text=sug, height=20, font=("Segoe UI", 9),
                                  fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                                  command=lambda s=sug: self._seleccionar_sugerencia(s))
            b_tag.pack(side="left", padx=2, pady=2)

        # Tabview Lateral (Estructura JSON / Resumen de Ramas)
        self.tabview_izq = ctk.CTkTabview(panel_izq, fg_color=COLOR_BG_CARD_LIGHT, corner_radius=10,
                                          segmented_button_selected_color=COLOR_ACCENT_PRIMARY,
                                          segmented_button_selected_hover_color=COLOR_ACCENT_HOVER)
        self.tabview_izq.grid(row=8, column=0, sticky="nsew", padx=18, pady=(0, 8))
        
        tab_json = self.tabview_izq.add("📝 Estructura JSON")
        tab_info = self.tabview_izq.add("📋 Resumen Texto")

        # Tab JSON
        tab_json.grid_columnconfigure(0, weight=1)
        tab_json.grid_rowconfigure(1, weight=1)

        f_json_btn = ctk.CTkFrame(tab_json, fg_color="transparent")
        f_json_btn.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ctk.CTkButton(f_json_btn, text="🔄 Redibujar Mapa", height=24, width=110,
                      font=("Segoe UI", 10, "bold"),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      border_width=1, border_color=COLOR_BORDER,
                      command=self.redibujar_desde_editor).pack(side="right")

        self.txt_estructura = ctk.CTkTextbox(tab_json, font=("Consolas", 10), wrap="none",
                                             fg_color=COLOR_BG_CARD, border_width=1,
                                             border_color=COLOR_BORDER, corner_radius=8)
        self.txt_estructura.grid(row=1, column=0, sticky="nsew")

        # Tab Info Texto
        tab_info.grid_columnconfigure(0, weight=1)
        tab_info.grid_rowconfigure(1, weight=1)
        
        f_info_btn = ctk.CTkFrame(tab_info, fg_color="transparent")
        f_info_btn.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ctk.CTkButton(f_info_btn, text="📋 Copiar Resumen", height=24, width=110,
                      font=("Segoe UI", 10, "bold"),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      border_width=1, border_color=COLOR_BORDER,
                      command=self.copiar_resumen_texto).pack(side="right")

        self.txt_resumen_texto = ctk.CTkTextbox(tab_info, font=("Segoe UI", 11), wrap="word",
                                                fg_color=COLOR_BG_CARD, border_width=1,
                                                border_color=COLOR_BORDER, corner_radius=8)
        self.txt_resumen_texto.grid(row=1, column=0, sticky="nsew")

        # Botones de Exportación
        frame_acciones = ctk.CTkFrame(panel_izq, fg_color="transparent")
        frame_acciones.grid(row=9, column=0, sticky="ew", padx=18, pady=(0, 14))
        frame_acciones.grid_columnconfigure((0, 1), weight=1)

        self.btn_exportar_word = ctk.CTkButton(frame_acciones, text="📄 Exportar a Word (.docx)", height=34,
                                               font=("Segoe UI", 11, "bold"),
                                               fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                                               state="disabled",
                                               command=self.exportar_word)
        self.btn_exportar_word.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_exportar_img = ctk.CTkButton(frame_acciones, text="🖼️ Guardar Imagen HD (.png)", height=34,
                                              font=("Segoe UI", 11, "bold"),
                                              fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
                                              state="disabled",
                                              command=self.exportar_imagen)
        self.btn_exportar_img.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # ── PANEL DERECHO: VISUALIZADOR HD & FICHAS DE ESTUDIO ──
        self.panel_der = ctk.CTkFrame(self, corner_radius=14, fg_color=COLOR_BG_CARD,
                                      border_width=1, border_color=COLOR_BORDER)
        self.panel_der.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.panel_der.grid_rowconfigure(1, weight=1)
        self.panel_der.grid_columnconfigure(0, weight=1)

        self.tabview_der = ctk.CTkTabview(self.panel_der, fg_color="transparent",
                                          segmented_button_selected_color=COLOR_ACCENT_PRIMARY,
                                          segmented_button_selected_hover_color=COLOR_ACCENT_HOVER)
        self.tabview_der.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

        tab_visual = self.tabview_der.add("🎨 Mapa Visual HD")
        tab_fichas = self.tabview_der.add("📖 Fichas & Estudio")

        # ── TAB 1: VISUALIZADOR MATPLOTLIB CON ZOOM & PAN ──
        tab_visual.grid_columnconfigure(0, weight=1)
        tab_visual.grid_rowconfigure(1, weight=1)

        bar_zoom = ctk.CTkFrame(tab_visual, fg_color=COLOR_BG_CARD_LIGHT, height=32, corner_radius=8,
                                border_width=1, border_color=COLOR_BORDER)
        bar_zoom.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ctk.CTkLabel(bar_zoom, text="🔍 Navegación:", font=("Segoe UI", 10, "bold"),
                     text_color=COLOR_TEXT_MUTED).pack(side="left", padx=(10, 6))

        ctk.CTkButton(bar_zoom, text="➕ Acercar", width=70, height=24, font=("Segoe UI", 9, "bold"),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      command=lambda: self._zoom_step(0.8)).pack(side="left", padx=2)

        ctk.CTkButton(bar_zoom, text="➖ Alejar", width=70, height=24, font=("Segoe UI", 9, "bold"),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      command=lambda: self._zoom_step(1.25)).pack(side="left", padx=2)

        ctk.CTkButton(bar_zoom, text="🔄 Centrar", width=70, height=24, font=("Segoe UI", 9, "bold"),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      command=self._reset_view).pack(side="left", padx=2)

        self.lbl_info_ramas = ctk.CTkLabel(bar_zoom, text="Sin mapa generado",
                                           font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_DIM)
        self.lbl_info_ramas.pack(side="right", padx=12)

        self.frame_canvas = ctk.CTkFrame(tab_visual, fg_color="#060913", corner_radius=10,
                                         border_width=1, border_color=COLOR_BORDER)
        self.frame_canvas.grid(row=1, column=0, sticky="nsew")
        self.frame_canvas.grid_rowconfigure(0, weight=1)
        self.frame_canvas.grid_columnconfigure(0, weight=1)

        self._inicializar_canvas()

        # ── TAB 2: FICHAS DE ESTUDIO INTERACTIVAS ──
        tab_fichas.grid_columnconfigure(0, weight=1)
        tab_fichas.grid_rowconfigure(0, weight=1)

        self.scroll_fichas = ctk.CTkScrollableFrame(tab_fichas, fg_color="transparent")
        self.scroll_fichas.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        
        self._mostrar_fichas_vacias()

    def _adjuntar_imagenes(self):
        rutas = filedialog.askopenfilenames(
            title="Seleccionar imágenes de apuntes / libros",
            filetypes=[
                ("Imágenes compatibles", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"),
                ("Todos los archivos", "*.*")
            ]
        )
        if rutas:
            for r in rutas:
                if r not in self.imagenes_adjuntas:
                    self.imagenes_adjuntas.append(r)
            self._actualizar_chips_imagenes()
            self._set_modelo("gemini")

    def _limpiar_imagenes(self):
        self.imagenes_adjuntas.clear()
        self._actualizar_chips_imagenes()

    def _eliminar_imagen(self, ruta):
        if ruta in self.imagenes_adjuntas:
            self.imagenes_adjuntas.remove(ruta)
            self._actualizar_chips_imagenes()

    def _actualizar_chips_imagenes(self):
        for w in self.scroll_img_chips.winfo_children():
            w.destroy()

        count = len(self.imagenes_adjuntas)
        self.lbl_img_count.configure(text=f"{count} foto{'s' if count != 1 else ''}")

        if not self.imagenes_adjuntas:
            ctk.CTkLabel(self.scroll_img_chips, text="Sin imágenes adjuntas",
                         font=("Segoe UI", 9), text_color=COLOR_TEXT_DIM).pack(side="left", padx=4)
            return

        for r in self.imagenes_adjuntas:
            nombre = os.path.basename(r)
            if len(nombre) > 16:
                nombre = nombre[:13] + "..."
            chip = ctk.CTkFrame(self.scroll_img_chips, fg_color=COLOR_BG_SURFACE, corner_radius=6)
            chip.pack(side="left", padx=2, pady=1)

            ctk.CTkLabel(chip, text=f"📷 {nombre}", font=("Segoe UI", 9), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=(4, 2))
            ctk.CTkButton(chip, text="✕", width=16, height=16, font=("Segoe UI", 8, "bold"),
                          fg_color="transparent", hover_color=COLOR_DANGER,
                          command=lambda path=r: self._eliminar_imagen(path)).pack(side="right", padx=2)

    def _seleccionar_sugerencia(self, tema):
        self.entry_tema.delete(0, "end")
        self.entry_tema.insert(0, tema)
        self.generar_mapa_mental()

    def _set_modelo(self, modelo):
        self.modelo_actual = modelo
        if modelo == "gemini":
            self.btn_gemini.configure(fg_color=COLOR_ACCENT_PRIMARY)
            self.btn_groq.configure(fg_color="transparent")
        else:
            self.btn_groq.configure(fg_color=COLOR_ACCENT_PURPLE)
            self.btn_gemini.configure(fg_color="transparent")

    def _inicializar_canvas(self):
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(16, 12), facecolor="#060913")
        self.ax.set_facecolor("#060913")
        
        self._orig_limits = MindMapRenderer.render(self.ax, {})

        self.canvas_grafico = FigureCanvasTkAgg(self.fig, master=self.frame_canvas)
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True)

        self.canvas_grafico.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas_grafico.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas_grafico.mpl_connect("motion_notify_event", self._on_mouse_motion)
        self.canvas_grafico.mpl_connect("scroll_event", self._on_mouse_scroll)

        self.canvas_grafico.draw()

    # ── EVENTOS INTERACTIVOS DE RATÓN (PAN & ZOOM) ──
    def _on_mouse_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.button in (1, 3):
            self._panning = True
            self._pan_start = (event.x, event.y)
            self._pan_start_limits = (self.ax.get_xlim(), self.ax.get_ylim())

    def _on_mouse_release(self, event):
        self._panning = False

    def _on_mouse_motion(self, event):
        if not self._panning or not self._pan_start_limits:
            return
        if event.x is None or event.y is None:
            return

        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]

        (x0, x1), (y0, y1) = self._pan_start_limits
        bbox = self.ax.get_window_extent()
        data_dx = (x1 - x0) * (dx / bbox.width)
        data_dy = (y1 - y0) * (dy / bbox.height)

        self.ax.set_xlim(x0 - data_dx, x1 - data_dx)
        self.ax.set_ylim(y0 - data_dy, y1 - data_dy)
        self.canvas_grafico.draw_idle()

    def _on_mouse_scroll(self, event):
        if event.inaxes != self.ax:
            return
        scale_factor = 0.85 if event.button == "up" else 1.18
        self._zoom_at(event.xdata, event.ydata, scale_factor)

    def _zoom_at(self, cur_x, cur_y, factor):
        if cur_x is None or cur_y is None:
            cur_x = (self.ax.get_xlim()[0] + self.ax.get_xlim()[1]) / 2.0
            cur_y = (self.ax.get_ylim()[0] + self.ax.get_ylim()[1]) / 2.0

        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        new_w = (x_max - x_min) * factor
        new_h = (y_max - y_min) * factor

        if new_w < 4.0 or new_w > 90.0:
            return

        rel_x = (cur_x - x_min) / (x_max - x_min)
        rel_y = (cur_y - y_min) / (y_max - y_min)

        self.ax.set_xlim(cur_x - new_w * rel_x, cur_x + new_w * (1 - rel_x))
        self.ax.set_ylim(cur_y - new_h * rel_y, cur_y + new_h * (1 - rel_y))
        self.canvas_grafico.draw_idle()

    def _zoom_step(self, factor):
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        cx = (x_min + x_max) / 2.0
        cy = (y_min + y_max) / 2.0
        self._zoom_at(cx, cy, factor)

    def _reset_view(self):
        if self._orig_limits:
            x0, x1, y0, y1 = self._orig_limits
            self.ax.set_xlim(x0, x1)
            self.ax.set_ylim(y0, y1)
            self.canvas_grafico.draw_idle()

    # ── GENERACIÓN CON INTELIGENCIA ARTIFICIAL ──
    def generar_mapa_mental(self):
        tema = self.entry_tema.get().strip()
        num_imgs = len(self.imagenes_adjuntas)

        if not tema and num_imgs == 0:
            messagebox.showwarning("Información requerida", "Introduce un tema o adjunta al menos una imagen de apuntes/libro.")
            return

        nivel = self.combo_nivel.get()
        enfoque = self.entry_enfoque.get().strip()

        self.btn_generar.configure(state="disabled")
        if num_imgs > 0:
            self.lbl_status.configure(text=f"📷 Analizando {num_imgs} imagen(es) con IA y creando mapa...", text_color=COLOR_ACCENT_CYAN)
        else:
            self.lbl_status.configure(text="✨ Creando estructura conceptual profunda...", text_color=COLOR_ACCENT_SKY)

        prompt_info = f"NIVEL EDUCATIVO: {nivel}\n"
        if tema:
            prompt_info += f"TEMA CENTRAL O TÍTULO SUGERIDO: {tema}\n"
        if enfoque:
            prompt_info += f"ENFOQUE Y PUNTOS CLAVE A PRIORIZAR: {enfoque}\n"

        threading.Thread(target=self._thread_generar_mapa, args=(prompt_info,), daemon=True).start()

    def _thread_generar_mapa(self, prompt_info):
        try:
            if self.imagenes_adjuntas:
                instruccion_extra = (
                    "INSTRUCCIÓN MULTIMODAL OBLIGATORIA:\n"
                    "Analiza minuciosamente todas las imágenes adjuntas (apuntes manuscritos o impresos, fotos de pizarra, esquemas, libros o diapositivas).\n"
                    "Extrae fielmente toda la información teórica, conceptos, definiciones, clasificaciones, fórmulas y relaciones que aparecen en las fotos.\n"
                    "Con esa base documental, construye el Mapa Conceptual exhaustivo según la estructura JSON solicitada."
                )
                full_prompt = f"{INSTRUCCIONES_MAPA_MENTAL}\n\n{instruccion_extra}\n\n{prompt_info}"
                respuesta = consultar_ia_multimodal(full_prompt, self.imagenes_adjuntas, modelo="gemini")
            else:
                full_prompt = f"{INSTRUCCIONES_MAPA_MENTAL}\n\n{prompt_info}"
                if self.modelo_actual == "gemini":
                    respuesta = llamar_gemini(full_prompt)
                else:
                    respuesta = llamar_groq(full_prompt)

            datos = self._extraer_json(respuesta)
            if not datos:
                t_nombre = self.entry_tema.get().strip() or "Tema Analizado"
                datos = self._generar_fallback_rico(t_nombre)

            self.after(0, lambda: self._mostrar_mapa_generado(datos))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error al Generar", f"No se pudo generar el mapa conceptual: {e}"))
        finally:
            self.after(0, lambda: [
                self.btn_generar.configure(state="normal"),
                self.lbl_status.configure(text="Listo", text_color=COLOR_SUCCESS)
            ])

    def _generar_fallback_rico(self, tema: str) -> dict:
        return {
            "tema_central": tema,
            "descripcion_general": f"Estudio conceptual y sistemático integral sobre {tema}, abarcando fundamentos, clasificación, mecanismos y aplicaciones.",
            "ramas": [
                {
                    "titulo": "1. ORIGEN & ANTECEDENTES",
                    "color": "#a855f7",
                    "sub_ramas": [
                        {
                            "titulo": "Bases Teóricas y Descubrimiento",
                            "puntos_detalle": [
                                f"Evolución histórica y primeros postulados fundamentales sobre {tema}.",
                                "Aportaciones de los principales investigadores y antecedentes formales."
                            ],
                            "conceptos_clave": ["Origen Histórico", "Marco Teórico"]
                        }
                    ]
                },
                {
                    "titulo": "2. ESTRUCTURA & COMPONENTES",
                    "color": "#f97316",
                    "sub_ramas": [
                        {
                            "titulo": "Arquitectura y Elementos Centrales",
                            "puntos_detalle": [
                                "Componentes constitutivos clave y organización interna.",
                                "Interrelaciones funcionales y flujos operativos."
                            ],
                            "conceptos_clave": ["Núcleo", "Organización"]
                        }
                    ]
                },
                {
                    "titulo": "3. CLASIFICACIÓN & TIPOLOGÍA",
                    "color": "#10b981",
                    "sub_ramas": [
                        {
                            "titulo": "Categorías Principales",
                            "puntos_detalle": [
                                "Taxonomía estándar y variantes de mayor impacto.",
                                "Criterios de diferenciación funcional y estructural."
                            ],
                            "conceptos_clave": ["Taxonomía", "Tipos"]
                        }
                    ]
                },
                {
                    "titulo": "4. MECANISMOS & FUNCIONES",
                    "color": "#ef4444",
                    "sub_ramas": [
                        {
                            "titulo": "Procesos Operativos",
                            "puntos_detalle": [
                                "Fases operativas, ciclos dinámicos y transformaciones.",
                                "Regulación, control y mecanismos de retroalimentación."
                            ],
                            "conceptos_clave": ["Procesos", "Regulación"]
                        }
                    ]
                },
                {
                    "titulo": "5. APLICACIONES PRÁCTICAS",
                    "color": "#06b6d4",
                    "sub_ramas": [
                        {
                            "titulo": "Implementación Real",
                            "puntos_detalle": [
                                "Casos de uso reales en la industria, academia y tecnología.",
                                "Impacto directo en la resolución de problemas actuales."
                            ],
                            "conceptos_clave": ["Casos Reales", "Impacto"]
                        }
                    ]
                }
            ]
        }

    def _extraer_json(self, texto):
        if not texto:
            return None
        texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL)
        texto = re.sub(r'```(?:think|thought).*?```', '', texto, flags=re.DOTALL)

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
        if match:
            candidato = match.group(1)
            try:
                return json.loads(candidato)
            except Exception:
                try:
                    c_limpio = re.sub(r',\s*([\]}])', r'\1', candidato)
                    return json.loads(c_limpio)
                except Exception:
                    pass

        start = texto.find("{")
        end = texto.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidato = texto[start:end+1]
            try:
                return json.loads(candidato)
            except Exception:
                try:
                    c_limpio = re.sub(r',\s*([\]}])', r'\1', candidato)
                    return json.loads(c_limpio)
                except Exception:
                    pass
        return None

    def _mostrar_mapa_generado(self, datos):
        self.datos_mapa = datos

        self.txt_estructura.delete("1.0", "end")
        self.txt_estructura.insert("end", json.dumps(datos, ensure_ascii=False, indent=2))

        resumen_md = self._generar_resumen_markdown(datos)
        self.txt_resumen_texto.delete("1.0", "end")
        self.txt_resumen_texto.insert("end", resumen_md)

        self._orig_limits = MindMapRenderer.render(self.ax, datos)
        self.canvas_grafico.draw()

        self._renderizar_fichas_estudio(datos)

        self.btn_exportar_word.configure(state="normal")
        self.btn_exportar_img.configure(state="normal")
        
        ramas_count = len(datos.get("ramas", []))
        total_subs = sum(len(r.get("sub_ramas", r.get("sub_conceptos", []))) for r in datos.get("ramas", []))
        self.lbl_info_ramas.configure(
            text=f"🧠 {ramas_count} Ejes • {total_subs} Tarjetas Informativas",
            text_color=COLOR_ACCENT_CYAN
        )

    def _generar_resumen_markdown(self, datos: dict) -> str:
        tema = datos.get("tema_central", "Tema Central")
        desc = datos.get("descripcion_general", "")
        lineas = [f"# 🧠 {tema}", ""]
        if desc:
            lineas.append(f"> {desc}")
            lineas.append("")

        for rama in datos.get("ramas", []):
            titulo = rama.get("titulo", "Rama")
            lineas.append(f"## 📌 {titulo}")
            if rama.get("descripcion"):
                lineas.append(f"*{rama.get('descripcion')}*")
                lineas.append("")

            subs = rama.get("sub_ramas", rama.get("sub_conceptos", []))
            for sub in subs:
                s_titulo = sub.get("titulo") or sub.get("nombre") or "Subtema"
                lineas.append(f"### 🔹 {s_titulo}")
                puntos = sub.get("puntos_detalle") or sub.get("puntos") or []
                if isinstance(puntos, str):
                    puntos = [puntos]
                detalle = sub.get("detalle")
                if detalle and not puntos:
                    puntos = [detalle]

                for p in puntos:
                    lineas.append(f"- {p}")

                claves = sub.get("conceptos_clave", [])
                if claves:
                    lineas.append(f"  *Conceptos clave:* `{', '.join(claves)}`")
                lineas.append("")

        return "\n".join(lineas)

    def _mostrar_fichas_vacias(self):
        for w in self.scroll_fichas.winfo_children():
            w.destroy()
        lbl = ctk.CTkLabel(self.scroll_fichas, text="Genera un mapa mental o sube fotos de apuntes para explorar las fichas pedagógicas.",
                           font=("Segoe UI", 12), text_color=COLOR_TEXT_DIM)
        lbl.pack(pady=40)

    def _renderizar_fichas_estudio(self, datos: dict):
        for w in self.scroll_fichas.winfo_children():
            w.destroy()

        tema = datos.get("tema_central", "Tema Central")
        desc = datos.get("descripcion_general", "")

        head_frame = ctk.CTkFrame(self.scroll_fichas, fg_color=COLOR_BG_CARD_LIGHT, corner_radius=12,
                                  border_width=1, border_color=COLOR_BORDER)
        head_frame.pack(fill="x", padx=6, pady=(4, 12))

        ctk.CTkLabel(head_frame, text=f"🌟 {tema}", font=("Segoe UI", 16, "bold"),
                     text_color=COLOR_ACCENT_SKY).pack(anchor="w", padx=16, pady=(12, 4))
        if desc:
            ctk.CTkLabel(head_frame, text=desc, font=("Segoe UI", 12),
                         text_color=COLOR_TEXT_MAIN, wraplength=560, justify="left").pack(anchor="w", padx=16, pady=(0, 12))

        for rama in datos.get("ramas", []):
            color = rama.get("color", COLOR_ACCENT_PRIMARY)
            r_title = rama.get("titulo", "Eje Temático")
            
            card_frame = ctk.CTkFrame(self.scroll_fichas, fg_color=COLOR_BG_CARD_LIGHT, corner_radius=12,
                                      border_width=1, border_color=color)
            card_frame.pack(fill="x", padx=6, pady=8)

            h_rama = ctk.CTkFrame(card_frame, fg_color="transparent")
            h_rama.pack(fill="x", padx=14, pady=(10, 6))

            ctk.CTkLabel(h_rama, text=f"📌 {r_title.upper()}", font=("Segoe UI", 13, "bold"),
                         text_color=color).pack(side="left")

            subs = rama.get("sub_ramas", rama.get("sub_conceptos", []))
            for sub in subs:
                s_title = sub.get("titulo") or sub.get("nombre") or "Subtema"
                
                sub_box = ctk.CTkFrame(card_frame, fg_color=COLOR_BG_SURFACE, corner_radius=8,
                                       border_width=1, border_color=COLOR_BORDER)
                sub_box.pack(fill="x", padx=12, pady=6)

                ctk.CTkLabel(sub_box, text=f"🔹 {s_title}", font=("Segoe UI", 11, "bold"),
                             text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=10, pady=(8, 4))

                puntos = sub.get("puntos_detalle") or sub.get("puntos") or []
                if isinstance(puntos, str):
                    puntos = [puntos]
                detalle = sub.get("detalle")
                if detalle and not puntos:
                    puntos = [detalle]

                for p in puntos:
                    ctk.CTkLabel(sub_box, text=f"• {p}", font=("Segoe UI", 10),
                                 text_color=COLOR_TEXT_MUTED, wraplength=520, justify="left").pack(anchor="w", padx=16, pady=1)

                claves = sub.get("conceptos_clave", [])
                if claves:
                    f_claves = ctk.CTkFrame(sub_box, fg_color="transparent")
                    f_claves.pack(fill="x", padx=14, pady=(4, 8))
                    ctk.CTkLabel(f_claves, text="🏷️ Claves: ", font=("Segoe UI", 9, "bold"),
                                 text_color=color).pack(side="left")
                    for cl in claves:
                        badge = ctk.CTkLabel(f_claves, text=f" {cl} ", font=("Segoe UI", 9),
                                             fg_color=COLOR_BG_CARD, corner_radius=4, text_color=COLOR_TEXT_MAIN)
                        badge.pack(side="left", padx=2)

    def redibujar_desde_editor(self):
        contenido = self.txt_estructura.get("1.0", "end-1c").strip()
        if not contenido:
            return
        try:
            datos = json.loads(contenido)
            self.datos_mapa = datos
            self._orig_limits = MindMapRenderer.render(self.ax, datos)
            self.canvas_grafico.draw()
            self._renderizar_fichas_estudio(datos)
            self.lbl_status.configure(text="Mapa visual actualizado", text_color=COLOR_SUCCESS)
        except Exception as e:
            messagebox.showerror("Error JSON", f"El formato JSON no es válido:\n{e}")

    def copiar_resumen_texto(self):
        txt = self.txt_resumen_texto.get("1.0", "end-1c").strip()
        if not txt:
            return
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo("Copiado", "Resumen pedagógico copiado al portapapeles con éxito.")

    def exportar_imagen(self):
        if not self.datos_mapa or not self.fig:
            messagebox.showwarning("Sin mapa", "Primero genera o redibuja un mapa mental.")
            return

        tema = self.datos_mapa.get("tema_central", "Mapa_Mental").replace(" ", "_")
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagen PNG HD", "*.png"), ("Todos los archivos", "*.*")],
            initialfile=f"MapaMental_{tema}_{datetime.now().strftime('%Y%m%d')}.png"
        )
        if not path:
            return

        try:
            fig_export, ax_export = plt.subplots(figsize=(24, 16), facecolor="#060913")
            MindMapRenderer.render(ax_export, self.datos_mapa)
            fig_export.savefig(path, dpi=300, bbox_inches="tight", facecolor="#060913", edgecolor="none")
            plt.close(fig_export)
            messagebox.showinfo("Imagen Guardada", f"Mapa mental exportado con éxito en Alta Definición (300 DPI):\n{path}")
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar la imagen:\n{e}")

    def exportar_word(self):
        if not self.datos_mapa:
            messagebox.showwarning("Sin mapa", "Primero genera o redibuja un mapa mental.")
            return

        tema = self.datos_mapa.get("tema_central", "Mapa Mental")
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Documento Word", "*.docx"), ("Todos los archivos", "*.*")],
            initialfile=f"MapaMental_{tema.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
        )
        if not path:
            return

        try:
            doc = Document()
            
            title_p = doc.add_heading(f"Mapa Conceptual: {tema}", 0)
            title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            meta_p = doc.add_paragraph(f"Nivel Académico: {self.combo_nivel.get()}  |  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            desc_gen = self.datos_mapa.get("descripcion_general", "")
            if desc_gen:
                p_res = doc.add_paragraph()
                r_bold = p_res.add_run("Resumen Conceptual General: ")
                r_bold.bold = True
                p_res.add_run(desc_gen)

            temp_img = os.path.expanduser("~/.temp_mapa_mental_export.png")
            fig_export, ax_export = plt.subplots(figsize=(24, 16), facecolor="#060913")
            MindMapRenderer.render(ax_export, self.datos_mapa)
            fig_export.savefig(temp_img, dpi=250, bbox_inches="tight", facecolor="#060913", edgecolor="none")
            plt.close(fig_export)

            doc.add_paragraph("")
            doc.add_heading("1. Esquema Gráfico del Mapa Conceptual", level=1)
            doc.add_picture(temp_img, width=Inches(6.4))
            doc.add_paragraph("")

            if os.path.exists(temp_img):
                os.remove(temp_img)

            doc.add_heading("2. Desglose Pedagógico Detallado por Ejes Temáticos", level=1)

            for i, rama in enumerate(self.datos_mapa.get("ramas", []), 1):
                r_title = rama.get("titulo", f"Eje {i}")
                doc.add_heading(f"{i}. {r_title}", level=2)
                
                if rama.get("descripcion"):
                    doc.add_paragraph(rama.get("descripcion"))

                subs = rama.get("sub_ramas", rama.get("sub_conceptos", []))
                if subs:
                    for sub in subs:
                        s_title = sub.get("titulo") or sub.get("nombre") or "Subtema"
                        doc.add_heading(f"▪ {s_title}", level=3)
                        
                        puntos = sub.get("puntos_detalle") or sub.get("puntos") or []
                        if isinstance(puntos, str):
                            puntos = [puntos]
                        detalle = sub.get("detalle")
                        if detalle and not puntos:
                            puntos = [detalle]

                        for p in puntos:
                            p_sub = doc.add_paragraph(style="List Bullet")
                            p_sub.add_run(str(p))

                        claves = sub.get("conceptos_clave", [])
                        if claves:
                            p_claves = doc.add_paragraph()
                            r_cl = p_claves.add_run("Términos Clave: ")
                            r_cl.bold = True
                            p_claves.add_run(", ".join(claves))

            doc.save(path)
            messagebox.showinfo("Exportado a Word", f"Documento Word profesional creado con éxito:\n{path}")
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo generar el documento Word:\n{e}")
