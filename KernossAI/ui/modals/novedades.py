"""
KernossAI - Ventana de Novedades y Notas de Versión
Resumen de mejoras y cambios generado por IA con síntesis de voz neuronal.
"""

import threading
import customtkinter as ctk
from tkinter import messagebox
from KernossAI.core.theme import (
    VERSION_APP,
    COLOR_BG_DARK,
    COLOR_BG_CARD,
    COLOR_BG_SURFACE,
    COLOR_BORDER,
    COLOR_ACCENT_PRIMARY,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_CYAN,
    COLOR_ACCENT_SKY,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_DANGER,
    aplicar_icono,
    centrar_ventana,
)
from KernossAI.core.i18n import t, obtener_idioma_activo
from KernossAI.core.auth import llamar_gemini, llamar_groq
from KernossAI.core.tts import tts_engine


class VentanaNovedadesIA(ctk.CTkToplevel):
    """Ventana modal interactiva con el resumen de novedades y cambios generado automáticamente por IA."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title(f"✨ Novedades y Cambios de Versión (v{VERSION_APP})")
        self.geometry("720x660")
        self.minsize(600, 520)
        self.configure(fg_color=COLOR_BG_DARK)
        self.transient(parent)
        self.grab_set()
        aplicar_icono(self)
        centrar_ventana(self, 720, 660)

        self._notas_cambios_detectadas = ""
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(header, text=f"✨ KernossAI v{VERSION_APP}",
                     font=("Segoe UI", 22, "bold"), text_color=COLOR_ACCENT_SKY).pack(anchor="w")
        ctk.CTkLabel(header, text=t("nov_subtitulo"),
                     font=("Segoe UI", 12), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        scroll_principal = ctk.CTkScrollableFrame(self, fg_color=COLOR_BG_CARD, corner_radius=14,
                                                 border_width=1, border_color=COLOR_BORDER)
        scroll_principal.pack(fill="both", expand=True, padx=25, pady=(5, 15))

        f_resumen_ia = ctk.CTkFrame(scroll_principal, fg_color=COLOR_BG_SURFACE, corner_radius=12,
                                   border_width=1, border_color=COLOR_ACCENT_CYAN)
        f_resumen_ia.pack(fill="x", padx=16, pady=(16, 12))

        f_hdr_ia = ctk.CTkFrame(f_resumen_ia, fg_color="transparent")
        f_hdr_ia.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(f_hdr_ia, text="🤖 " + t("nov_tit_resumen_ia"),
                     font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")

        self.btn_tts_novedades = ctk.CTkButton(
            f_hdr_ia, text="🔊 Escuchar", font=("Segoe UI", 11, "bold"),
            fg_color=COLOR_BG_SURFACE, hover_color=COLOR_BORDER, width=95, height=28,
            command=self._toggle_tts
        )
        self.btn_tts_novedades.pack(side="right", padx=(6, 0))

        self.btn_resumir_ia = ctk.CTkButton(
            f_hdr_ia, text="⚡ " + t("nov_btn_analizar_ia"), font=("Segoe UI", 11, "bold"),
            fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER, width=120, height=28,
            command=self._generar_resumen_ia
        )
        self.btn_resumir_ia.pack(side="right")

        self.txt_resumen_ia = ctk.CTkTextbox(
            f_resumen_ia, font=("Segoe UI", 11), height=110, wrap="word",
            fg_color=COLOR_BG_DARK, border_width=1, border_color=COLOR_BORDER
        )
        self.txt_resumen_ia.pack(fill="x", padx=14, pady=(0, 14))
        self.txt_resumen_ia.insert("1.0", t("nov_placeholder_ia"))
        self.txt_resumen_ia.configure(state="disabled")

        ctk.CTkLabel(scroll_principal, text="📋 " + t("nov_tit_desglose"),
                     font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=16, pady=(4, 8))

        self.txt_notas_oficiales = ctk.CTkTextbox(
            scroll_principal, font=("Consolas", 11), height=220, wrap="word",
            fg_color=COLOR_BG_DARK, border_width=1, border_color=COLOR_BORDER
        )
        self.txt_notas_oficiales.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.txt_notas_oficiales.insert("1.0", self._obtener_notas_cambios())
        self.txt_notas_oficiales.configure(state="disabled")

        f_footer = ctk.CTkFrame(self, fg_color="transparent")
        f_footer.pack(fill="x", padx=25, pady=(0, 18))

        ctk.CTkButton(
            f_footer, text=t("nov_btn_entendido"), font=("Segoe UI", 12, "bold"),
            fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
            height=38, command=self._cerrar
        ).pack(fill="x")

    def _obtener_notas_cambios(self):
        idioma = obtener_idioma_activo()
        notas_map = {
            "es": (
                f"KERNOSSAI — VERSIÓN OFICIAL v{VERSION_APP}\n"
                "─────────────────────────────────────────────────────────────\n"
                "🌐 1. NUEVO MÓDULO: GLOBAL CLASSROOMS & MODEL UNITED NATIONS\n"
                "   • Búsqueda Masiva Web 360° en tiempo real (evidencias, tratados, resoluciones ONU).\n"
                "   • Redactor de Position Papers oficiales en formato canónico de 3 secciones.\n"
                "   • Generador de Opening Speeches cronometrados a 1 minuto (~120 palabras) con contador de palabras y estimación de tiempo.\n"
                "   • Creación de Borradores de Resolución (Draft Resolutions) con cláusulas preambulatorias y operativas.\n"
                "   • Matriz estratégica de Alianzas, Bloques y Oposición (Bloc Matrix).\n"
                "   • Simulador de Preguntas Hostiles (POIs) con réplicas diplomáticas documentadas.\n"
                "   • Botón de ayuda interactiva '?' con guía diplomática completa de cada herramienta.\n"
                "   • Exportación directa a Word (.docx), copia al portapapeles y voz neural Edge-TTS.\n\n"
                "👑 2. SISTEMA AVANZADO DE ROLES Y PERMISOS\n"
                "   • Nuevos rangos: Alumno, Profesor, Alumno+, Profesor+ y Admin.\n"
                "   • Acceso exclusivo al módulo Global Classrooms para Alumno+, Profesor+ y Admin.\n"
                "   • Modal informativo para rangos estándar con enlace a Soporte Oficial.\n\n"
                "🛡️ 3. GESTIÓN INTEGRAL EN MODERACIÓN & BANS\n"
                "   • Selector interactivo de rangos en vivo para cada usuario registrado.\n"
                "   • Barra de desplazamiento horizontal en cada tarjeta por si el correo o HWID es extenso.\n"
                "   • Asignación manual de roles por correo en Supabase y Render.\n\n"
                "📜 4. POLÍTICA DE PRIVACIDAD & CUMPLIMIENTO RGPD VINCULANTE\n"
                "   • Consentimiento obligatorio al iniciar la app: continuar o salir.\n"
                "   • Cláusulas legales estrictas sobre tratamiento legítimo de IPs para seguridad y anti-ataques.\n"
                "   • Obligatoriedad de aceptación en el registro y acceso permanente desde Ajustes.\n\n"
                "⚙️ 5. INTERFAZ Y COMPILACIÓN MULTIPLATAFORMA\n"
                "   • Sidebar con scroll central y pie fijo para 'Ajustes' y 'Cerrar Sesión'.\n"
                "   • Motor de IA ultra-resiliente con fallback Gemini / Groq.\n"
                "   • Compilación nativa (.dmg para macOS, instalador .exe para Windows, Linux tar.gz / PKGBUILD)."
            ),
            "en": (
                f"KERNOSSAI — OFFICIAL RELEASE v{VERSION_APP}\n"
                "─────────────────────────────────────────────────────────────\n"
                "🌐 1. NEW MODULE: GLOBAL CLASSROOMS & MODEL UNITED NATIONS\n"
                "   • Real-time 360° Massive Web Research (UN resolutions, treaties, stats).\n"
                "   • Official Position Paper generator (3 canonical sections).\n"
                "   • Timed Opening Speeches (1 minute / ~120 words) with word count and duration estimator.\n"
                "   • UN Draft Resolution generator with preambulatory and operative clauses.\n"
                "   • Strategic Bloc Matrix (Allies, Opponents, and Negotiating Blocs).\n"
                "   • Hostile Questions Simulator (POIs) with diplomatic rebuttals.\n"
                "   • Interactive '?' guide button explaining every tool.\n"
                "   • Direct Word (.docx) export, clipboard copy, and Edge-TTS voice playback.\n\n"
                "👑 2. ADVANCED ROLES & PERMISSIONS SYSTEM\n"
                "   • Institutional roles: Student, Teacher, Student+, Teacher+, Admin.\n"
                "   • Exclusive Global Classrooms access for Student+, Teacher+, and Admin.\n\n"
                "🛡️ 3. FULL MODERATION & BANS CONTROL\n"
                "   • Live interactive role assignment per user.\n"
                "   • Horizontal scrollbar per card for long email addresses or HWIDs.\n\n"
                "📜 4. BINDING PRIVACY POLICY & GDPR COMPLIANCE\n"
                "   • Mandatory consent on app startup with strict IP security clauses.\n"
                "   • Permanent access from Settings and registration requirement.\n\n"
                "⚙️ 5. UI & MULTI-PLATFORM BUILDS\n"
                "   • Scrollable sidebar with fixed footer for Settings and Logout.\n"
                "   • Resilient AI engine (Gemini & Groq fallback).\n"
                "   • Native packages (.dmg for macOS, .exe Setup for Windows, Linux tar.gz / PKGBUILD)."
            ),
            "de": (
                f"KERNOSSAI — OFFIZIELLE VERSION v{VERSION_APP}\n"
                "─────────────────────────────────────────────────────────────\n"
                "🌐 1. NEUES MODUL: GLOBAL CLASSROOMS & MODEL UNITED NATIONS\n"
                "   • 360° Echtzeit-Websuche für UN-Resolutionen, Verträge und Statistiken.\n"
                "   • Offizielle Position Papers (3 Abschnitte) & 1-Minuten-Eröffnungsreden.\n"
                "   • UN-Resolutionsentwürfe, Bündnismatrizen und POI-Angriffssimulator.\n\n"
                "👑 2. ERWEITERTES ROLLEN- & RECHTESYSTEM\n"
                "   • Neue Ränge: Schüler, Lehrer, Schüler+, Lehrer+, Admin.\n"
                "   • Exklusiver Zugriff auf Global Classrooms für Schüler+, Lehrer+ und Admin.\n\n"
                "🛡️ 3. MODERATION & DATENSCHUTZ (DSGVO)\n"
                "   • Horizontale Bildlaufleiste für lange E-Mail-Adressen in der Benutzerliste.\n"
                "   • Verbindliche Datenschutzerklärung beim App-Start mit IP-Sicherheitsklauseln."
            ),
            "fr": (
                f"KERNOSSAI — VERSION OFFICIELLE v{VERSION_APP}\n"
                "─────────────────────────────────────────────────────────────\n"
                "🌐 1. NOUVEAU MODULE: GLOBAL CLASSROOMS & MODEL UNITED NATIONS\n"
                "   • Recherche Web 360° en temps réel (traités de l'ONU, résolutions, statistiques).\n"
                "   • Générateur de Position Papers officiels (3 sections) et discours chronométrés (1 min).\n"
                "   • Résolutions ONU, matrice d'alliances et simulateur de questions hostiles (POIs).\n\n"
                "👑 2. SYSTÈME DE RÔLES ET PERMISSIONS\n"
                "   • Rangs: Élève, Professeur, Élève+, Professeur+, Admin.\n"
                "   • Accès exclusif à Global Classrooms pour Élève+, Professeur+ et Admin.\n\n"
                "🛡️ 3. MODÉRATION & RGPD OBLIGATOIRE\n"
                "   • Barre de défilement horizontale par carte pour les adresses e-mail longues.\n"
                "   • Politique de confidentialité et consentement RGPD au lancement de l'application."
            )
        }
        return notas_map.get(idioma, notas_map["es"])

    def _generar_resumen_ia(self):
        self.btn_resumir_ia.configure(state="disabled", text="Analizando...")
        self.txt_resumen_ia.configure(state="normal")
        self.txt_resumen_ia.delete("1.0", "end")
        self.txt_resumen_ia.insert("1.0", "🤖 Analizando las mejoras reales de esta versión...")
        self.txt_resumen_ia.configure(state="disabled")
        threading.Thread(target=self._thread_ia_resumen, daemon=True).start()

    def _thread_ia_resumen(self):
        try:
            notas = self._obtener_notas_cambios()
            idioma = obtener_idioma_activo()
            nombres_idioma = {"es": "Español", "en": "English", "de": "Deutsch", "fr": "Français"}
            idioma_str = nombres_idioma.get(idioma, "Español")

            prompt = (
                f"Eres el asistente oficial de KernossAI. El usuario acaba de abrir la app en la versión v{VERSION_APP}.\n\n"
                f"Estas son las novedades implementadas:\n'''\n{notas}\n'''\n\n"
                "Explica de forma concisa y directa (máximo 120-150 palabras) las mejoras clave y da 1 consejo de estudio.\n"
                f"Responde exclusivamente en el idioma: {idioma_str}."
            )
            try:
                resumen = llamar_gemini(prompt)
            except Exception:
                resumen = llamar_groq(prompt)

            def _actualizar():
                try:
                    if not self.winfo_exists():
                        return
                    self.txt_resumen_ia.configure(state="normal")
                    self.txt_resumen_ia.delete("1.0", "end")
                    self.txt_resumen_ia.insert("1.0", resumen)
                    self.txt_resumen_ia.configure(state="disabled")
                    self.btn_resumir_ia.configure(state="normal", text="🔄 Reanalizar")
                except Exception:
                    pass

            self.after(0, _actualizar)
        except Exception as e:
            try:
                if self.winfo_exists():
                    self.after(0, lambda: messagebox.showerror("Error IA", str(e)))
                    self.after(0, lambda: self.btn_resumir_ia.configure(state="normal", text="⚡ Analizar con IA"))
            except Exception:
                pass

    def _toggle_tts(self):
        if tts_engine.esta_reproduciendo():
            tts_engine.detener()
            self.btn_tts_novedades.configure(text="🔊 Escuchar", fg_color=COLOR_BG_SURFACE)
        else:
            texto = self.txt_resumen_ia.get("1.0", "end-1c").strip()
            if not texto or texto.startswith("🤖") or texto.startswith("⏳"):
                return

            def _cb(rep):
                if rep:
                    self.btn_tts_novedades.configure(text="⏹️ Detener", fg_color=COLOR_DANGER)
                else:
                    self.btn_tts_novedades.configure(text="🔊 Escuchar", fg_color=COLOR_BG_SURFACE)

            tts_engine.hablar(texto, callback_estado=lambda r: self.after(0, lambda: _cb(r)))

    def _cerrar(self):
        tts_engine.detener()
        self.destroy()
