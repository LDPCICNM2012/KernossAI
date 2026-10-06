"""
KernossAI - Módulo: Global Classrooms & Model United Nations (MUN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Motor integral de investigación masiva 360°, inteligencia diplomática,
generación de Position Papers oficiales, discursos de apertura cronometrados,
borradores de resolución de la ONU y simulador de preguntas hostiles (POIs).
Acceso exclusivo para delegados y docentes con rango Alumno+, Profesor+ y Admin.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import re
import json
import urllib.parse
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

import requests
import customtkinter as ctk
from tkinter import messagebox, filedialog
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from KernossAI.core.theme import (
    COLOR_BG_DARK,
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
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    centrar_ventana,
    aplicar_icono,
)
from KernossAI.core.auth import consultar_ia, limpiar_respuesta_ia
from KernossAI.core.tts import tts_engine


RUTA_HISTORIAL_GC = os.path.expanduser("~/.historial_global_classrooms.json")

HEADERS_NAVEGADOR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7",
}


# ── Motor de Búsqueda Masiva en Tiempo Real ─────────────────────────

def _buscar_duckduckgo_api(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    try:
        from duckduckgo_search import DDGS
        resultados = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                resultados.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", "")
                })
        return resultados
    except Exception:
        return []


def _buscar_duckduckgo_html(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    resultados = []
    try:
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query}
        resp = requests.post(url, data=data, headers=HEADERS_NAVEGADOR, timeout=8)
        if resp.status_code == 200:
            patron = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
            coincidencias = re.findall(patron, resp.text, re.DOTALL)
            for raw_href, raw_title in coincidencias[:max_results]:
                clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
                parsed = urllib.parse.urlparse(raw_href)
                params = urllib.parse.parse_qs(parsed.query)
                real_url = params.get("uddg", [raw_href])[0]
                resultados.append({
                    "title": clean_title,
                    "snippet": "",
                    "url": real_url
                })
    except Exception:
        pass
    return resultados


def _buscar_wikipedia(query: str, lang: str = "es", max_results: int = 3) -> List[Dict[str, str]]:
    resultados = []
    try:
        endpoint = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": max_results,
            "utf8": 1
        }
        r = requests.get(endpoint, params=params, headers=HEADERS_NAVEGADOR, timeout=6)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("query", {}).get("search", []):
                snippet_limpio = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
                title = item.get("title", "")
                page_url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                resultados.append({
                    "title": f"Wikipedia: {title}",
                    "snippet": snippet_limpio,
                    "url": page_url
                })
    except Exception:
        pass
    return resultados


def _ejecutar_busqueda_individual(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    res = _buscar_duckduckgo_api(query, max_results=max_results)
    if not res:
        res = _buscar_duckduckgo_html(query, max_results=max_results)
    return res


def busqueda_masiva_global_classrooms(pais: str, topic: str, comite: str = "", idioma: str = "es") -> Dict[str, Any]:
    pais_clean = pais.strip()
    topic_clean = topic.strip()
    comite_str = f" {comite.strip()}" if comite else ""

    queries = [
        f"{pais_clean} official foreign policy on {topic_clean} United Nations OR EU",
        f"{pais_clean} stance position paper {topic_clean} Model UN Global Classrooms{comite_str}",
        f"{pais_clean} international treaties signed resolutions {topic_clean}",
        f"{pais_clean} permanent representative ambassador statements speeches {topic_clean}",
        f"{pais_clean} allies adversaries voting bloc diplomacy {topic_clean}",
        f"{pais_clean} statistics data facts {topic_clean}",
    ]

    if idioma.lower().startswith("es"):
        queries.extend([
            f"postura de {pais_clean} sobre {topic_clean} ONU declaraciones oficiales",
            f"{pais_clean} tratados internacionales ratificados sobre {topic_clean}",
            f"{pais_clean} politica exterior posicion diplomática {topic_clean}"
        ])

    todos_los_resultados: List[Dict[str, str]] = []
    urls_vistas = set()

    with ThreadPoolExecutor(max_workers=6) as executor:
        futuros = {executor.submit(_ejecutar_busqueda_individual, q, 4): q for q in queries}
        futuro_wiki_pais = executor.submit(_buscar_wikipedia, f"Relaciones exteriores de {pais_clean}", "es", 2)
        futuro_wiki_topic = executor.submit(_buscar_wikipedia, f"{pais_clean} {topic_clean}", "es", 2)

        for f in as_completed(futuros):
            try:
                res_lista = f.result()
                for r in res_lista:
                    url = r.get("url", "")
                    if url and url not in urls_vistas:
                        urls_vistas.add(url)
                        todos_los_resultados.append(r)
            except Exception:
                pass

        for fw in [futuro_wiki_pais, futuro_wiki_topic]:
            try:
                for r in fw.result():
                    url = r.get("url", "")
                    if url and url not in urls_vistas:
                        urls_vistas.add(url)
                        todos_los_resultados.append(r)
            except Exception:
                pass

    bloques_texto = []
    fuentes_utilizadas = []
    for i, res in enumerate(todos_los_resultados[:25], start=1):
        titulo = res.get("title", "Fuente Oficial")
        snippet = res.get("snippet", "")
        url = res.get("url", "")
        bloques_texto.append(f"[{i}] {titulo}\nSnippet: {snippet}\nFuente: {url}\n")
        fuentes_utilizadas.append({"titulo": titulo, "url": url, "snippet": snippet})

    corpus_web = "\n".join(bloques_texto) if bloques_texto else "No se pudieron obtener fragmentos web en directo. Usando conocimiento diplomático consolidado."

    return {
        "pais": pais_clean,
        "topic": topic_clean,
        "comite": comite.strip(),
        "total_fuentes": len(todos_los_resultados),
        "corpus_web": corpus_web,
        "fuentes": fuentes_utilizadas
    }


# ── Clase Principal del Módulo ──────────────────────────────────────

class ModuloGlobalClassrooms(ctk.CTkFrame):
    """Módulo interactivo de preparación y asistencia para Global Classrooms / Model UN."""

    def __init__(self, master, sesion=None):
        super().__init__(master, fg_color="transparent")
        self.sesion = sesion or {}
        self._investigando = False
        self._datos_actuales: Dict[str, Any] = {}
        self._audio_reproduciendo = False

        self._build_ui()
        self._cargar_historial_en_selector()

    def _build_ui(self):
        # ── Cabecera del Módulo ──
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        header.pack(fill="x", padx=16, pady=(10, 8))

        f_tit = ctk.CTkFrame(header, fg_color="transparent")
        f_tit.pack(side="left", padx=18, pady=12)

        ctk.CTkLabel(
            f_tit, text="🌐 Global Classrooms & Model United Nations",
            font=("Segoe UI", 18, "bold"), text_color=COLOR_ACCENT_SKY
        ).pack(anchor="w")

        ctk.CTkLabel(
            f_tit,
            text="Inteligencia Diplomática 360°, Búsqueda Masiva en Fuentes Oficiales de la ONU, Position Papers & Debate",
            font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        # Badge de rango en cabecera
        f_badge = ctk.CTkFrame(header, fg_color="transparent")
        f_badge.pack(side="right", padx=18, pady=12)

        mi_rol = self.sesion.get("rol", "Alumno+")
        ctk.CTkLabel(
            f_badge, text=f"⭐ Acceso Premium: {mi_rol}",
            font=("Segoe UI", 11, "bold"), text_color="#38bdf8",
            fg_color="#0c2d48", corner_radius=8, padx=10, pady=4
        ).pack(side="right")

        btn_guia = ctk.CTkButton(
            f_badge, text="❓ ¿Para qué sirve cada cosa? (Guía)",
            font=("Segoe UI", 11, "bold"), height=32,
            fg_color="#4338ca", hover_color="#3730a3",
            border_width=1, border_color="#818cf8",
            command=self._abrir_guia_explicativa
        )
        btn_guia.pack(side="right", padx=(0, 10))

        # ── Tarjeta de Configuración de la Delegación ──
        card_inputs = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        card_inputs.pack(fill="x", padx=16, pady=(0, 8))

        f_grid = ctk.CTkFrame(card_inputs, fg_color="transparent")
        f_grid.pack(fill="x", padx=16, pady=12)
        f_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1. País
        ctk.CTkLabel(f_grid, text="🏳️ País Asignado:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=4, pady=(0, 2))
        self.entry_pais = ctk.CTkEntry(f_grid, placeholder_text="ej: Alemania, Japón, Brasil, Francia...", font=("Segoe UI", 11), height=34, fg_color=COLOR_BG_CARD_LIGHT, border_color=COLOR_BORDER)
        self.entry_pais.grid(row=1, column=0, sticky="ew", padx=4)

        # 2. Topic / Tema
        ctk.CTkLabel(f_grid, text="📌 Topic / Tema del Debate:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).grid(row=0, column=1, sticky="w", padx=4, pady=(0, 2))
        self.entry_topic = ctk.CTkEntry(f_grid, placeholder_text="ej: Regulación ética de la IA, Refugiados climáticos...", font=("Segoe UI", 11), height=34, fg_color=COLOR_BG_CARD_LIGHT, border_color=COLOR_BORDER)
        self.entry_topic.grid(row=1, column=1, sticky="ew", padx=4)

        # 3. Comité de la ONU
        ctk.CTkLabel(f_grid, text="🏛️ Comité u Órgano de la ONU:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).grid(row=0, column=2, sticky="w", padx=4, pady=(0, 2))
        self.combo_comite = ctk.CTkComboBox(
            f_grid,
            values=[
                "Asamblea General (GA / General Assembly)",
                "Consejo de Seguridad (UNSC / Security Council)",
                "UNICEF (Fondo para la Infancia)",
                "ACNUR (UNHCR / Agencia de Refugiados)",
                "UNESCO (Educación, Ciencia y Cultura)",
                "Consejo de Derechos Humanos (UNHRC)",
                "PNUD (UNDP / Desarrollo Sostenible)",
                "OMS / WHO (Organización Mundial de la Salud)",
                "Comisión Europea / Consejo de la UE"
            ],
            font=("Segoe UI", 11), height=34, fg_color=COLOR_BG_CARD_LIGHT, border_color=COLOR_BORDER
        )
        self.combo_comite.set("Asamblea General (GA / General Assembly)")
        self.combo_comite.grid(row=1, column=2, sticky="ew", padx=4)

        # 4. Idioma Diplomático
        ctk.CTkLabel(f_grid, text="🌐 Idioma Diplomático:", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_MAIN).grid(row=0, column=3, sticky="w", padx=4, pady=(0, 2))
        self.combo_idioma = ctk.CTkOptionMenu(
            f_grid,
            values=["Español Diplomático", "Formal English (Model UN)"],
            font=("Segoe UI", 11, "bold"), height=34,
            fg_color=COLOR_ACCENT_PRIMARY, button_color=COLOR_ACCENT_HOVER
        )
        self.combo_idioma.set("Español Diplomático")
        self.combo_idioma.grid(row=1, column=3, sticky="ew", padx=4)

        # ── Botones de Modos de Generación ──
        f_botones = ctk.CTkFrame(card_inputs, fg_color="transparent")
        f_botones.pack(fill="x", padx=16, pady=(4, 12))

        self.btn_dossier = ctk.CTkButton(
            f_botones, text="🚀 Dossier 360° Masivo", height=36,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_CYAN,
            hover_color=COLOR_ACCENT_CYAN_HOVER, text_color="#000",
            command=lambda: self._iniciar_generacion("dossier")
        )
        self.btn_dossier.pack(side="left", padx=(0, 6), expand=True, fill="x")

        self.btn_paper = ctk.CTkButton(
            f_botones, text="📄 Position Paper Oficial", height=36,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_PRIMARY,
            hover_color=COLOR_ACCENT_HOVER,
            command=lambda: self._iniciar_generacion("paper")
        )
        self.btn_paper.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_speech = ctk.CTkButton(
            f_botones, text="🎤 Opening Speech (~1 min)", height=36,
            font=("Segoe UI", 11, "bold"), fg_color="#7c3aed",
            hover_color="#6d28d9",
            command=lambda: self._iniciar_generacion("speech")
        )
        self.btn_speech.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_resolucion = ctk.CTkButton(
            f_botones, text="📜 Borrador de Resolución", height=36,
            font=("Segoe UI", 11, "bold"), fg_color="#059669",
            hover_color="#047857",
            command=lambda: self._iniciar_generacion("resolucion")
        )
        self.btn_resolucion.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_bloques = ctk.CTkButton(
            f_botones, text="🤝 Alianzas & Oposición", height=36,
            font=("Segoe UI", 11, "bold"), fg_color="#b45309",
            hover_color="#92400e",
            command=lambda: self._iniciar_generacion("bloques")
        )
        self.btn_bloques.pack(side="left", padx=4, expand=True, fill="x")

        self.btn_ataques = ctk.CTkButton(
            f_botones, text="⚔️ Simulador POIs / Ataques", height=36,
            font=("Segoe UI", 11, "bold"), fg_color="#be123c",
            hover_color="#9f1239",
            command=lambda: self._iniciar_generacion("ataques")
        )
        self.btn_ataques.pack(side="left", padx=(4, 0), expand=True, fill="x")

        # ── Barra de Progreso y Estado ──
        self.f_progreso = ctk.CTkFrame(self, fg_color="transparent")
        self.f_progreso.pack(fill="x", padx=16, pady=(0, 4))

        self.lbl_estado = ctk.CTkLabel(
            self.f_progreso, text="💡 Listo. Introduce el país y el topic del debate y selecciona qué documento diplomático deseas generar.",
            font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED, anchor="w"
        )
        self.lbl_estado.pack(side="left", fill="x", expand=True)

        self.pbar = ctk.CTkProgressBar(self.f_progreso, height=6, fg_color=COLOR_BG_CARD, progress_color=COLOR_ACCENT_CYAN)
        self.pbar.set(0.0)
        self.pbar.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # ── TabView Principal de Salida ──
        self.tabview = ctk.CTkTabview(self, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(4, 6))

        self.tab_dossier = self.tabview.add("🌐 Dossier 360°")
        self.tab_paper = self.tabview.add("📄 Position Paper")
        self.tab_speech = self.tabview.add("🎤 Opening Speech")
        self.tab_resolucion = self.tabview.add("📜 Draft Resolution")
        self.tab_bloques = self.tabview.add("🤝 Alianzas & Opositores")
        self.tab_ataques = self.tabview.add("⚔️ Simulador POIs")
        self.tab_fuentes = self.tabview.add("🔗 Fuentes Web")

        # Cuadros de texto para cada pestaña
        self.txt_dossier = self._crear_textbox(self.tab_dossier)
        self.txt_paper = self._crear_textbox(self.tab_paper)
        self.txt_speech = self._crear_textbox(self.tab_speech)
        self.txt_resolucion = self._crear_textbox(self.tab_resolucion)
        self.txt_bloques = self._crear_textbox(self.tab_bloques)
        self.txt_ataques = self._crear_textbox(self.tab_ataques)
        self.txt_fuentes = self._crear_textbox(self.tab_fuentes)

        # ── Barra Inferior de Herramientas y Exportación ──
        footer = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, height=48, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        footer.pack(fill="x", padx=16, pady=(0, 10))

        # Contador de palabras / tiempo para el speech
        self.lbl_stats = ctk.CTkLabel(
            footer, text="📊 Palabras: 0  |  ⏱️ Tiempo estimado: 0s",
            font=("Segoe UI", 11, "bold"), text_color=COLOR_ACCENT_SKY
        )
        self.lbl_stats.pack(side="left", padx=16)

        # Historial dropdown
        self.combo_historial = ctk.CTkOptionMenu(
            footer, values=["🕒 Investigaciones Recientes"],
            font=("Segoe UI", 10), width=210, height=32,
            fg_color=COLOR_BG_CARD_LIGHT, button_color=COLOR_BORDER,
            command=self._cargar_desde_historial
        )
        self.combo_historial.pack(side="left", padx=10)

        # Botones de exportación
        btn_word = ctk.CTkButton(
            footer, text="📄 Exportar a Word (.docx)", height=32,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_ACCENT_PRIMARY,
            hover_color=COLOR_ACCENT_HOVER, command=self._exportar_word
        )
        btn_word.pack(side="right", padx=(4, 16))

        btn_copiar = ctk.CTkButton(
            footer, text="📋 Copiar Pestaña", height=32, width=120,
            font=("Segoe UI", 11, "bold"), fg_color=COLOR_BG_SURFACE,
            hover_color=COLOR_ACCENT_HOVER, command=self._copiar_al_portapapeles
        )
        btn_copiar.pack(side="right", padx=4)

        btn_audio = ctk.CTkButton(
            footer, text="🔊 Escuchar Discurso", height=32, width=140,
            font=("Segoe UI", 11, "bold"), fg_color="#4f46e5",
            hover_color="#4338ca", command=self._escuchar_speech
        )
        btn_audio.pack(side="right", padx=4)

    def _crear_textbox(self, parent):
        txt = ctk.CTkTextbox(
            parent, font=("Consolas", 12), wrap="word",
            fg_color=COLOR_BG_CARD_LIGHT, border_width=1, border_color=COLOR_BORDER
        )
        txt.pack(fill="both", expand=True, padx=6, pady=6)
        txt.insert("1.0", "Introduce un país y un topic y presiona cualquiera de los botones de investigación para comenzar.")
        return txt

    # ── Lógica de Generación e Investigación Masiva ─────────────────────

    def _iniciar_generacion(self, modo: str):
        if self._investigando:
            messagebox.showwarning("Proceso Activo", "Ya hay una investigación diplomática en curso.")
            return

        pais = self.entry_pais.get().strip()
        topic = self.entry_topic.get().strip()
        comite = self.combo_comite.get().strip()
        idioma = "en" if "English" in self.combo_idioma.get() else "es"

        if not pais or not topic:
            messagebox.showwarning("Campos Requeridos", "Por favor introduce al menos el País Asignado y el Topic del debate.")
            return

        self._investigando = True
        self.pbar.configure(mode="indeterminate")
        self.pbar.start()

        threading.Thread(
            target=self._hilo_generacion,
            args=(pais, topic, comite, idioma, modo),
            daemon=True
        ).start()

    def _hilo_generacion(self, pais: str, topic: str, comite: str, idioma: str, modo: str):
        try:
            self._actualizar_estado(f"🌐 [1/2] Realizando búsqueda masiva web sobre '{pais}' y '{topic}'...")

            # 1. Búsqueda web en paralelo
            datos_busqueda = busqueda_masiva_global_classrooms(pais, topic, comite, idioma)
            fuentes = datos_busqueda.get("fuentes", [])

            self._actualizar_estado(f"🧠 [2/2] {len(fuentes)} fuentes encontradas. Redactando con IA especializada...")

            # 2. Construir prompt especializado según el modo
            prompt = self._construir_prompt(pais, topic, comite, idioma, modo, datos_busqueda.get("corpus_web", ""))

            # 3. Llamar a la IA con resiliencia
            resultado = consultar_ia(prompt, modelo="gemini")
            resultado_limpio = limpiar_respuesta_ia(resultado)

            # 4. Actualizar interfaz según el modo
            self.after(0, lambda: self._finalizar_generacion(pais, topic, comite, modo, resultado_limpio, fuentes))

        except Exception as e:
            self.after(0, lambda: self._error_generacion(str(e)))

    def _construir_prompt(self, pais: str, topic: str, comite: str, idioma: str, modo: str, corpus_web: str) -> str:
        es_en = (idioma == "en")
        idioma_regla = (
            "IMPORTANT: Write the ENTIRE document in formal, professional DIPLOMATIC ENGLISH as used in Model United Nations (MUN) conferences."
            if es_en else
            "IMPORTANTE: Redacta TODO el documento en ESPAÑOL DIPLOMÁTICO formal y protocolario de Modelo de Naciones Unidas (MUN)."
        )

        base_contexto = f"""
Eres un Asesor Senior de Asuntos Exteriores y Diplomacia Internacional especializado en Global Classrooms y Model United Nations (MUN).
DELEGACIÓN ASIGNADA: {pais.upper()}
TEMA / TOPIC: {topic}
COMITÉ: {comite}
{idioma_regla}

EVIDENCIA RECOPILADA EN LA BÚSQUEDA WEB EN TIEMPO REAL:
{corpus_web}
"""

        if modo == "dossier":
            return base_contexto + f"""
Genera el DOSSIER DIPLOMÁTICO 360° MÁS COMPLETO POSIBLE para {pais}.
Estructura en Markdown:
# 🌐 DOSSIER OFICIAL DE DELEGACIÓN: {pais.upper()}
## Topic: {topic} | Comité: {comite}

### 1. 📌 FICHA GEOPOLÍTICA & IDENTIDAD NACIONAL
- Capital, sistema de gobierno y líder actual.
- Organizaciones y bloques a los que pertenece (ONU, UE, OTAN, BRICS, G77, etc.).
- Principios rectores de su política exterior.

### 2. 🏛️ POSTURA OFICIAL RESPECTO AL TEMA ({topic.upper()})
- Visión fundamental de {pais}.
- Líneas rojas (aspectos innegociables).
- Prioridades estratégicas.

### 3. 📜 ANTECEDENTES Y MARCO JURÍDICO INTERNACIONAL
- Tratados y resoluciones clave firmados o rechazados por {pais}.
- Historial de votaciones en la Asamblea General / Consejo de Seguridad.
- Leyes y programas nacionales destacados.

### 4. 📊 ESTADÍSTICAS & DATOS DE IMPACTO
- Al menos 5 datos numéricos precisos con años y fuentes para sustentar argumentos.

### 5. 🗺️ MAPA DE ALIANZAS Y OPONENTES
- Aliados naturales (Bloque de redacción).
- Países rivales y motivos de conflicto diplomático.
- Delegaciones neutrales clave a convencer.

### 6. 📝 PROPUESTAS DE CLÁUSULAS OPERATIVAS (RESOLUCIÓN)
- Al menos 4 cláusulas operativas con verbos oficiales (Urges, Calls upon, Recommends...).

### 7. 🛡️ DEFENSA DIPLOMÁTICA & ATAQUES PREVISIBLES
- Críticas que recibirá {pais} y la respuesta diplomática óptima sin salirse del personaje.
"""

        elif modo == "paper":
            return base_contexto + f"""
Redacta el POSITION PAPER OFICIAL en el formato canónico estricto de 3 secciones de Model United Nations para {pais}:

# 📄 OFFICIAL POSITION PAPER
**Committee:** {comite}
**Topic:** {topic}
**Country:** {pais}

### I. Background of the Topic
(Explicación del problema a escala global, relevancia internacional y desafíos urgentes).

### II. Country Policy & Past Actions
(Qué ha hecho específicamente {pais}: tratados ratificados, inversión económica, legislación nacional y votaciones previas en la ONU).

### III. Proposed Solutions & Policy Recommendations
(Propuestas realistas, viables y ambiciosas que la delegación de {pais} promoverá durante el debate y en la resolución).
"""

        elif modo == "speech":
            return base_contexto + f"""
Escribe el OPENING SPEECH (Discurso de Apertura) para la delegación de {pais}.
REQUISITOS CRÍTICOS:
- Duración exacta: 60 segundos (~110 a 130 palabras).
- Comienza con el saludo protocolario formal ("Honorable Chairs, distinguished delegates...").
- Estructura:
  1. Un Hook contundente (cita impactante o dato conmovedor).
  2. La postura firme e identidad soberana de {pais}.
  3. Un llamado a la acción dirigido a los aliados ("Call to action").
- Finaliza cediendo el tiempo a la mesa ("The delegation of {pais} yields its time to the Chair / to questions").
Al final, indica:
[Recuento de palabras: X | Tiempo estimado de lectura: ~55 segundos]
"""

        elif modo == "resolucion":
            return base_contexto + f"""
Redacta un BORRADOR DE RESOLUCIÓN (Draft Resolution) de la ONU formal propuesto por la delegación de {pais}:
# 📜 DRAFT RESOLUTION
**Committee:** {comite}
**Topic:** {topic}
**Sponsors:** {pais}, [Aliados clave recomendados]
**Signatories:** [Estados miembros interesados]

Estructura obligatoria:
### Preambulatory Clauses (Cláusulas Preambulatorias):
(Al menos 4-5 cláusulas comenzando con verbos en cursiva: *Affirming, Deeply concerned, Guided by, Emphasizing, Recalling...*)

### Operative Clauses (Cláusulas Operativas):
(Al menos 6-8 cláusulas numeradas comenzando con verbos en cursiva: *1. Calls upon, 2. Urges, 3. Recommends, 4. Decides to establish, 5. Requests...*)
"""

        elif modo == "bloques":
            return base_contexto + f"""
Elabora la MATRIZ ESTRATÉGICA DE ALIANZAS, BLOQUES Y OPONENTES (Bloc Matrix) para {pais} sobre {topic}:
# 🤝 MATRIZ DIPLOMÁTICA DE BLOQUES: {pais.upper()}

### 1. 🟢 ALIADOS NATURALES (Sponsors potenciales de la resolución)
- Países con los que {pais} debe unirse en los unmoderated caucuses y por qué comparten intereses.

### 2. 🔴 BLOQUE OPOSITOR / ANTAGÓNICO
- Países que atacarán la postura de {pais} y los argumentos con los que intentarán desacreditarte.

### 3. 🟡 PAÍSES OSCILANTES O INDECISOS (Swing States)
- Países que se pueden persuadir mediante concesiones diplomáticas para sumar votos.

### 4. 🎯 ESTRATEGIA DE NEGOCIACIÓN
- Qué concesiones puede hacer {pais} y cuáles son sus líneas rojas absolutas.
"""

        elif modo == "ataques":
            return base_contexto + f"""
Genera un SIMULADOR DE PREGUNTAS HOSTILES (Points of Information & Cross-Examination) para {pais} sobre {topic}:
# ⚔️ SIMULADOR DE ATAQUES Y PREGUNTAS INCÓMODAS

Para cada una de las 4 situaciones más difíciles o hipocresías que otros países le pueden reprochar a {pais}:
1. ❓ **Ataque / Pregunta de la delegación rival:** (Pregunta agresiva y directa de un oponente).
2. 🛡️ **Respuesta Diplomática Maestra:** (Respuesta elegante, documentada, manteniendo la compostura y defendiendo los intereses nacionales).
"""
        return base_contexto

    def _finalizar_generacion(self, pais: str, topic: str, comite: str, modo: str, resultado: str, fuentes: list):
        self._investigando = False
        self.pbar.stop()
        self.pbar.configure(mode="determinate")
        self.pbar.set(1.0)

        self._datos_actuales[modo] = resultado
        self._datos_actuales["pais"] = pais
        self._datos_actuales["topic"] = topic
        self._datos_actuales["comite"] = comite
        self._datos_actuales["fuentes"] = fuentes

        # Asignar texto a la pestaña correspondiente
        tab_map = {
            "dossier": (self.tab_dossier, self.txt_dossier, "🌐 Dossier 360°"),
            "paper": (self.tab_paper, self.txt_paper, "📄 Position Paper"),
            "speech": (self.tab_speech, self.txt_speech, "🎤 Opening Speech"),
            "resolucion": (self.tab_resolucion, self.txt_resolucion, "📜 Draft Resolution"),
            "bloques": (self.tab_bloques, self.txt_bloques, "🤝 Alianzas & Opositores"),
            "ataques": (self.tab_ataques, self.txt_ataques, "⚔️ Simulador POIs")
        }

        if modo in tab_map:
            tab_obj, txt_obj, tab_name = tab_map[modo]
            txt_obj.delete("1.0", "end")
            txt_obj.insert("1.0", resultado)
            self.tabview.set(tab_name)

        # Actualizar fuentes
        if fuentes:
            self.txt_fuentes.delete("1.0", "end")
            f_text = f"🔗 FUENTES Y ANTECEDENTES EXTRAÍDOS DE LA WEB ({len(fuentes)} fuentes):\n\n"
            for i, f in enumerate(fuentes, 1):
                f_text += f"[{i}] {f.get('titulo')}\n    URL: {f.get('url')}\n    Snippet: {f.get('snippet', '')}\n\n"
            self.txt_fuentes.insert("1.0", f_text)

        # Actualizar estadísticas de palabras y tiempo
        self._actualizar_estadisticas_texto(resultado)

        # Guardar en historial local
        self._guardar_historial(pais, topic, comite, modo)

        self.lbl_estado.configure(
            text=f"✅ Documento generado exitosamente para la delegación de {pais} sobre '{topic}'.",
            text_color=COLOR_SUCCESS
        )

    def _actualizar_estadisticas_texto(self, texto: str):
        palabras = len(texto.split())
        # Promedio hablado: ~130 palabras por minuto (~2.1 palabras por segundo)
        segundos = int(palabras / 2.1) if palabras > 0 else 0
        minutos = segundos // 60
        seg_rest = segundos % 60
        tiempo_str = f"{minutos}m {seg_rest}s" if minutos > 0 else f"{segundos}s"
        self.lbl_stats.configure(text=f"📊 Palabras: {palabras:,}  |  ⏱️ Lectura estimada: ~{tiempo_str}")

    def _error_generacion(self, error_msg: str):
        self._investigando = False
        self.pbar.stop()
        self.pbar.configure(mode="determinate")
        self.pbar.set(0.0)
        self.lbl_estado.configure(text=f"❌ Error al generar: {error_msg}", text_color=COLOR_DANGER)
        messagebox.showerror("Error de Investigación", f"No se pudo completar la generación: {error_msg}")

    def _actualizar_estado(self, texto: str):
        self.after(0, lambda: self.lbl_estado.configure(text=texto, text_color=COLOR_ACCENT_CYAN))

    # ── Exportación y Acciones Auxiliares ────────────────────────────────

    def _exportar_word(self):
        tab_actual = self.tabview.get()
        txt_map = {
            "🌐 Dossier 360°": self.txt_dossier,
            "📄 Position Paper": self.txt_paper,
            "🎤 Opening Speech": self.txt_speech,
            "📜 Draft Resolution": self.txt_resolucion,
            "🤝 Alianzas & Opositores": self.txt_bloques,
            "⚔️ Simulador POIs": self.txt_ataques,
            "🔗 Fuentes Web": self.txt_fuentes,
        }
        textbox = txt_map.get(tab_actual, self.txt_dossier)
        contenido = textbox.get("1.0", "end").strip()

        if not contenido or contenido.startswith("Introduce un país"):
            messagebox.showwarning("Sin Contenido", "No hay contenido generado para exportar.")
            return

        pais = self.entry_pais.get().strip() or "Delegacion"
        topic = self.entry_topic.get().strip() or "Topic"
        nombre_defecto = f"KernossAI_GC_{pais}_{tab_actual[:8].strip().replace(' ', '_')}.docx"

        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=nombre_defecto,
            filetypes=[("Documentos Word", "*.docx"), ("Todos los archivos", "*.*")]
        )
        if not ruta_guardado:
            return

        try:
            doc = Document()
            # Encabezado institucional
            p_head = doc.add_paragraph()
            p_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_head = p_head.add_run("GLOBAL CLASSROOMS & MODEL UNITED NATIONS")
            r_head.bold = True
            r_head.font.size = Pt(16)
            r_head.font.color.rgb = RGBColor(0x0a, 0x47, 0x8a)

            p_sub = doc.add_paragraph()
            p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_sub = p_sub.add_run(f"Dossier Oficial de la Delegación: {pais.upper()} | {tab_actual}\nTema: {topic}")
            r_sub.font.size = Pt(11)
            r_sub.font.italic = True

            doc.add_paragraph("─" * 45)

            # Contenido en párrafos
            for linea in contenido.split("\n"):
                linea_strip = linea.strip()
                if linea_strip.startswith("# "):
                    h = doc.add_heading(linea_strip[2:], level=1)
                elif linea_strip.startswith("## "):
                    h = doc.add_heading(linea_strip[3:], level=2)
                elif linea_strip.startswith("### "):
                    h = doc.add_heading(linea_strip[4:], level=3)
                elif linea_strip.startswith("- "):
                    p = doc.add_paragraph(linea_strip[2:], style='List Bullet')
                else:
                    doc.add_paragraph(linea)

            doc.save(ruta_guardado)
            messagebox.showinfo("Exportación Exitosa", f"Documento Word guardado en:\n{ruta_guardado}")
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo Word: {e}")

    def _copiar_al_portapapeles(self):
        tab_actual = self.tabview.get()
        txt_map = {
            "🌐 Dossier 360°": self.txt_dossier,
            "📄 Position Paper": self.txt_paper,
            "🎤 Opening Speech": self.txt_speech,
            "📜 Draft Resolution": self.txt_resolucion,
            "🤝 Alianzas & Opositores": self.txt_bloques,
            "⚔️ Simulador POIs": self.txt_ataques,
            "🔗 Fuentes Web": self.txt_fuentes,
        }
        textbox = txt_map.get(tab_actual, self.txt_dossier)
        contenido = textbox.get("1.0", "end").strip()

        if contenido:
            self.clipboard_clear()
            self.clipboard_append(contenido)
            messagebox.showinfo("Copiado", f"El contenido de '{tab_actual}' se ha copiado al portapapeles.")

    def _escuchar_speech(self):
        speech_text = self.txt_speech.get("1.0", "end").strip()
        if not speech_text or speech_text.startswith("Introduce un país"):
            messagebox.showwarning("Sin Discurso", "Primero genera el Opening Speech para escucharlo.")
            return

        # Limpiar metadatos
        texto_a_leer = re.sub(r"\[Recuento de palabras.*?\]", "", speech_text, flags=re.IGNORECASE)
        texto_a_leer = re.sub(r"#+.*", "", texto_a_leer)

        def _thread():
            idioma = "en" if "English" in self.combo_idioma.get() else "es"
            voz = "en-US-JennyNeural" if idioma == "en" else "es-ES-AlvaroNeural"
            tts_engine.speak(texto_a_leer.strip(), voice=voz)

        threading.Thread(target=_thread, daemon=True).start()

    # ── Gestión de Historial Local ──────────────────────────────────────

    def _guardar_historial(self, pais: str, topic: str, comite: str, modo: str):
        item = {
            "pais": pais,
            "topic": topic,
            "comite": comite,
            "modo": modo,
            "fecha": datetime.now().strftime("%d/%m %H:%M")
        }
        try:
            historial = []
            if os.path.exists(RUTA_HISTORIAL_GC):
                with open(RUTA_HISTORIAL_GC, "r", encoding="utf-8") as f:
                    historial = json.load(f)
            # Evitar duplicados consecutivos
            historial = [h for h in historial if not (h.get("pais") == pais and h.get("topic") == topic and h.get("modo") == modo)]
            historial.insert(0, item)
            historial = historial[:20]
            with open(RUTA_HISTORIAL_GC, "w", encoding="utf-8") as f:
                json.dump(historial, f, ensure_ascii=False, indent=2)
            self._cargar_historial_en_selector()
        except Exception:
            pass

    def _cargar_historial_en_selector(self):
        try:
            if os.path.exists(RUTA_HISTORIAL_GC):
                with open(RUTA_HISTORIAL_GC, "r", encoding="utf-8") as f:
                    historial = json.load(f)
                valores = [f"{h.get('pais')} - {h.get('topic')[:20]}... ({h.get('fecha')})" for h in historial]
                if valores:
                    self.combo_historial.configure(values=["🕒 Investigaciones Recientes"] + valores)
        except Exception:
            pass

    def _cargar_desde_historial(self, seleccion: str):
        if seleccion == "🕒 Investigaciones Recientes":
            return
        try:
            if os.path.exists(RUTA_HISTORIAL_GC):
                with open(RUTA_HISTORIAL_GC, "r", encoding="utf-8") as f:
                    historial = json.load(f)
                for h in historial:
                    tag = f"{h.get('pais')} - {h.get('topic')[:20]}... ({h.get('fecha')})"
                    if tag == seleccion:
                        self.entry_pais.delete(0, "end")
                        self.entry_pais.insert(0, h.get("pais", ""))
                        self.entry_topic.delete(0, "end")
                        self.entry_topic.insert(0, h.get("topic", ""))
                        if h.get("comite"):
                            self.combo_comite.set(h.get("comite"))
                        break
        except Exception:
            pass

    def _abrir_guia_explicativa(self):
        ModalGuiaGlobalClassrooms(self)


# ── Modal de Guía Explicativa de Global Classrooms ─────────────────

class ModalGuiaGlobalClassrooms(ctk.CTkToplevel):
    """Guía interactiva que explica detalladamente qué es cada función del módulo Global Classrooms."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("❓ Guía de Herramientas — Global Classrooms & Model UN")
        self.geometry("840x680")
        self.minsize(680, 520)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        self.grab_set()
        aplicar_icono(self)
        centrar_ventana(self, 840, 680)

        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, height=65, corner_radius=0)
        header.pack(fill="x")

        f_ht = ctk.CTkFrame(header, fg_color="transparent")
        f_ht.pack(side="left", padx=20, pady=12)
        ctk.CTkLabel(f_ht, text="❓ Guía Completa de Global Classrooms & Model UN",
                     font=("Segoe UI", 16, "bold"), text_color=COLOR_ACCENT_SKY).pack(anchor="w")
        ctk.CTkLabel(f_ht, text="Aprende para qué sirve cada herramienta diplomática y cómo destacar en tu conferencia.",
                     font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED).pack(anchor="w")

        ctk.CTkButton(header, text="✕", width=36, height=36, fg_color=COLOR_BG_CARD,
                      hover_color=COLOR_DANGER, font=("Segoe UI", 13, "bold"), command=self.destroy).pack(side="right", padx=16)

        scroll = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_CARD, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        scroll.pack(fill="both", expand=True, padx=20, pady=(15, 12))

        secciones = [
            ("🌐 ¿Qué es Global Classrooms & Model UN (MUN)?",
             "Es la simulación oficial de la Organización de las Naciones Unidas (ONU) y la Unión Europea para estudiantes. Cada delegación representa a un país soberano y debe defender su política exterior, debatir según las Reglas de Procedimiento parlamentarias y negociar resoluciones vinculantes sin abandonar su papel."),

            ("🚀 1. Búsqueda Masiva & Dossier 360°",
             "¿Para qué sirve? Realiza un rastreo en tiempo real en la web oficial (ONU, tratados bilaterales, estadísticas del Banco Mundial, declaraciones de embajadores).\n"
             "• Genera la radiografía integral del país: principios rectores, líneas rojas innegociables, datos estadísticos clave y argumentos históricos de impacto."),

            ("📄 2. Position Paper Oficial (Formato Canónico ONU)",
             "¿Para qué sirve? Es el documento formal indispensable que toda delegación debe entregar a la presidencia (Chairs) antes de la conferencia.\n"
             "• Estructurado estrictamente en las 3 secciones oficiales:\n"
             "  I. Background of the Topic (diagnóstico global del problema).\n"
             "  II. Country Policy & Past Actions (tratados ratificados, leyes nacionales y votaciones previas).\n"
             "  III. Proposed Solutions (propuestas realistas y viables que tu país promoverá)."),

            ("🎤 3. Opening Speech (~1 minuto cronometrado)",
             "¿Para qué sirve? Es tu discurso de presentación ante la asamblea plenaria.\n"
             "• Calibrado a exactamente 60 segundos (~110-130 palabras) para que no te corte la mesa.\n"
             "• Estructura retórica: Saludo formal ('Honorable Chairs, distinguished delegates...'), un gancho conmovedor (Hook), la postura firme de tu país y un llamamiento a la acción (Call to action).\n"
             "• Incluye contador de palabras, estimación de tiempo en vivo y reproducción de voz con Edge-TTS."),

            ("📜 4. Borrador de Resolución (Draft Resolution)",
             "¿Para qué sirve? El documento legislativo definitivo que se negocia y vota en la comisión.\n"
             "• Cláusulas Preambulatorias: Justifican la resolución (verbos en cursiva: Affirming, Deeply concerned, Guided by...).\n"
             "• Cláusulas Operativas: Acciones concretas, mandatos y asignación de fondos (verbos en cursiva: Calls upon, Urges, Recommends, Decides...)."),

            ("🤝 5. Matriz de Alianzas y Oponentes (Bloc Matrix)",
             "¿Para qué sirve? Es tu mapa táctico para las sesiones de negociación no moderada (unmoderated caucuses).\n"
             "• Aliados Naturales: Países con intereses comunes para formar bloque y copatrocinar la resolución.\n"
             "• Bloque Antagónico: Delegaciones que atacarán tu postura y argumentos que utilizarán.\n"
             "• Países Oscilantes (Swing States): Delegaciones indecisas a las que puedes convencer mediante concesiones diplomáticas."),

            ("⚔️ 6. Simulador de Ataques Hostiles (POIs - Points of Information)",
             "¿Para qué sirve? Entrena tus réplicas ante preguntas trampa y ataques dialécticos de rivales.\n"
             "• Te anticipa las contradicciones de tu país (derechos humanos, emisiones, gasto de defensa) y te proporciona la réplica diplomática elegante y documentada para defenderte sin salirte del personaje."),

            ("💾 7. Exportación a Word (.docx) y Voz Neural (Edge-TTS)",
             "¿Para qué sirve? Permite exportar cualquier documento a formato Word con encabezado oficial para imprimir o llevar a la sala, copiar al portapapeles y practicar tu pronunciación en inglés diplomático mediante lectura en voz alta.")
        ]

        for titulo, desc in secciones:
            f_card = ctk.CTkFrame(scroll, fg_color=COLOR_BG_CARD_LIGHT, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
            f_card.pack(fill="x", padx=10, pady=6)

            ctk.CTkLabel(f_card, text=titulo, font=("Segoe UI", 13, "bold"), text_color=COLOR_ACCENT_SKY).pack(anchor="w", padx=14, pady=(10, 4))
            ctk.CTkLabel(f_card, text=desc, font=("Segoe UI", 11), text_color=COLOR_TEXT_MAIN, justify="left", wraplength=720).pack(anchor="w", padx=14, pady=(0, 10))

        btn_entendido = ctk.CTkButton(self, text="Entendido, Volver a la Delegación", height=38,
                                      font=("Segoe UI", 12, "bold"), fg_color=COLOR_ACCENT_PRIMARY,
                                      hover_color=COLOR_ACCENT_HOVER, command=self.destroy)
        btn_entendido.pack(fill="x", padx=20, pady=(0, 16))
