"""
KernossAI - Módulo: Resumidor Inteligente de Textos, PDFs e Imágenes
Síntesis académica avanzada con IA multimodal (extracción OCR y análisis visual de fotos/apuntes),
control de temas, progreso visual, lectura de voz TTS y exportación a Word.
"""

import os
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from docx import Document
from docx.shared import Inches, Pt
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
from KernossAI.core.tts import tts_engine


class ModuloResumidor(ctk.CTkFrame):
    """Módulo de resumen y síntesis conceptual con LLM multimodal y lectura de voz."""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.modelo_actual = "gemini"
        self.imagenes_adjuntas = []
        self.instrucciones = (
            "Eres un pedagogo y redactor académico de élite. Tu objetivo es sintetizar y estructurar la información "
            "de manera profunda, rigurosa, clara y exhaustiva.\n\n"
            "ESTRUCTURA DEL RESUMEN:\n"
            "1. TÍTULO Y CONCEPTO CLAVE: Definición formal y marco general.\n"
            "2. IDEAS Y POSTULADOS PRINCIPALES: Desglose temático con viñetas explicativas y datos concretos.\n"
            "3. CAUSAS, MECANISMOS O CONTEXTO: Cómo funciona o qué factores intervienen.\n"
            "4. CONSECUENCIAS, APLICACIONES O CONCLUSIONES: Impacto práctico y síntesis final.\n"
            "5. GLOSARIO DE TÉRMINOS CLAVE: 3 a 5 conceptos destacados con breve explicación.\n\n"
            "No inventes datos. Mantén el rigor académico y la máxima claridad."
        )
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        
        ctk.CTkLabel(header, text=t("resum_titulo"),
                     font=("Segoe UI", 26, "bold"), text_color=COLOR_ACCENT_SKY).pack(side="left")
        
        # Switch de Modelo
        frame_model = ctk.CTkFrame(header, fg_color=COLOR_BG_CARD_LIGHT,
                                   border_width=1, border_color=COLOR_BORDER, corner_radius=8)
        frame_model.pack(side="right", padx=10)

        self.btn_gemini = ctk.CTkButton(frame_model, text="🧠 Gemini (Visión)", height=28, width=100,
                                        font=("Segoe UI", 10, "bold"),
                                        fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                                        command=lambda: self._set_modelo("gemini"))
        self.btn_gemini.pack(side="left", padx=2, pady=2)

        self.btn_groq = ctk.CTkButton(frame_model, text="⚡ Groq", height=28, width=70,
                                      font=("Segoe UI", 10, "bold"),
                                      fg_color="transparent", hover_color=COLOR_ACCENT_PURPLE_HOVER,
                                      command=lambda: self._set_modelo("groq"))
        self.btn_groq.pack(side="left", padx=2, pady=2)

        self.entry_nombre = ctk.CTkEntry(
            header, placeholder_text="Título / Materia del resumen...", width=220,
            height=32, font=("Segoe UI", 11),
            fg_color=COLOR_BG_CARD, text_color=COLOR_TEXT_MAIN,
            placeholder_text_color=COLOR_TEXT_DIM, border_color=COLOR_BORDER
        )
        self.entry_nombre.pack(side="right", padx=10)

        # Contenedor Principal (2 Columnas: Entrada / Salida)
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, padx=20, sticky="nsew")
        main.grid_columnconfigure(0, weight=5)
        main.grid_columnconfigure(1, weight=6)
        main.grid_rowconfigure(0, weight=1)

        # ── COLUMNA IZQUIERDA: ENTRADA DE TEXTO & SUBIDA DE IMÁGENES ──
        input_f = ctk.CTkFrame(main, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=14)
        input_f.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        input_f.grid_rowconfigure(2, weight=1)
        input_f.grid_columnconfigure(0, weight=1)

        # Cabecera de Entrada
        f_in_top = ctk.CTkFrame(input_f, fg_color="transparent")
        f_in_top.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

        ctk.CTkLabel(f_in_top, text=t("resum_lbl_entrada"), font=("Segoe UI", 13, "bold"),
                     text_color=COLOR_TEXT_MAIN).pack(side="left")

        self.lbl_conteo_caracteres = ctk.CTkLabel(f_in_top, text="0 caracteres", font=("Segoe UI", 10),
                                                 text_color=COLOR_TEXT_MUTED)
        self.lbl_conteo_caracteres.pack(side="right")

        # Barra de Subida de Imágenes Multimodal
        f_img_box = ctk.CTkFrame(input_f, fg_color=COLOR_BG_CARD_LIGHT, corner_radius=10,
                                 border_width=1, border_color=COLOR_BORDER)
        f_img_box.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        f_img_header = ctk.CTkFrame(f_img_box, fg_color="transparent")
        f_img_header.pack(fill="x", padx=10, pady=(6, 4))

        ctk.CTkLabel(f_img_header, text="📷 Imágenes de Apuntes / Páginas de Libro:",
                     font=("Segoe UI", 11, "bold"), text_color=COLOR_ACCENT_CYAN).pack(side="left")

        self.lbl_img_status = ctk.CTkLabel(f_img_header, text="0 fotos", font=("Segoe UI", 10),
                                          text_color=COLOR_TEXT_MUTED)
        self.lbl_img_status.pack(side="right")

        f_img_actions = ctk.CTkFrame(f_img_box, fg_color="transparent")
        f_img_actions.pack(fill="x", padx=10, pady=(0, 6))

        self.btn_adjuntar_img = ctk.CTkButton(f_img_actions, text="📁 Subir Varias Fotos", height=28,
                                              font=("Segoe UI", 11, "bold"),
                                              fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                                              border_width=1, border_color=COLOR_BORDER,
                                              command=self._adjuntar_imagenes)
        self.btn_adjuntar_img.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_extraer_ocr = ctk.CTkButton(f_img_actions, text="🔍 Extraer Texto", height=28, width=110,
                                            font=("Segoe UI", 10, "bold"),
                                            fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_CYAN_HOVER,
                                            border_width=1, border_color=COLOR_BORDER,
                                            command=self._extraer_texto_imagenes)
        self.btn_extraer_ocr.pack(side="left", padx=(0, 4))

        self.btn_limpiar_img = ctk.CTkButton(f_img_actions, text="🗑️", width=32, height=28,
                                             font=("Segoe UI", 11),
                                             fg_color=COLOR_BG_SURFACE, hover_color=COLOR_DANGER,
                                             border_width=1, border_color=COLOR_BORDER,
                                             command=self._limpiar_imagenes)
        self.btn_limpiar_img.pack(side="right")

        # Scroll / Chips de imágenes
        self.scroll_img_chips = ctk.CTkScrollableFrame(f_img_box, fg_color="transparent", height=38, orientation="horizontal")
        self.scroll_img_chips.pack(fill="x", padx=8, pady=(0, 6))
        self._actualizar_chips_imagenes()

        # Cuadro de Texto de Entrada
        self.txt_input = ctk.CTkTextbox(input_f, font=("Segoe UI", 12), fg_color=COLOR_BG_CARD_LIGHT, wrap="word")
        self.txt_input.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 14))
        self.txt_input.bind("<KeyRelease>", self._actualizar_conteo)

        # ── COLUMNA DERECHA: RESUMEN GENERADO & HERRAMIENTAS ──
        output_f = ctk.CTkFrame(main, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER, corner_radius=14)
        output_f.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        output_f.grid_rowconfigure(1, weight=1)
        output_f.grid_columnconfigure(0, weight=1)

        f_out_top = ctk.CTkFrame(output_f, fg_color="transparent")
        f_out_top.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

        ctk.CTkLabel(f_out_top, text=t("resum_lbl_salida"), font=("Segoe UI", 13, "bold"),
                     text_color=COLOR_ACCENT_CYAN).pack(side="left")

        ctk.CTkButton(f_out_top, text="📋 Copiar", height=24, width=70, font=("Segoe UI", 10, "bold"),
                      fg_color=COLOR_BG_SURFACE, hover_color=COLOR_ACCENT_HOVER,
                      border_width=1, border_color=COLOR_BORDER,
                      command=self._copiar_salida).pack(side="right")

        self.txt_output = ctk.CTkTextbox(output_f, font=("Segoe UI", 12), fg_color=COLOR_BG_CARD_LIGHT, wrap="word")
        self.txt_output.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 14))

        # Footer con Progreso y Botones de Acción
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, padx=20, pady=16, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(footer, progress_color=COLOR_ACCENT_CYAN)
        self.progress_bar.pack(fill="x", pady=(0, 12))
        self.progress_bar.set(0)

        f_btn_row = ctk.CTkFrame(footer, fg_color="transparent")
        f_btn_row.pack(fill="x")

        self.btn_procesar = ctk.CTkButton(f_btn_row, text=t("resum_btn_resumir"),
                                          height=42, font=("Segoe UI", 13, "bold"),
                                          fg_color=COLOR_ACCENT_PRIMARY, hover_color=COLOR_ACCENT_HOVER,
                                          command=self.iniciar_proceso)
        self.btn_procesar.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_tts_resumen = ctk.CTkButton(f_btn_row, text=t("btn_escuchar"), height=42, width=140,
                                            font=("Segoe UI", 12, "bold"),
                                            fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_ACCENT_CYAN,
                                            hover_color=COLOR_ACCENT_HOVER,
                                            command=self._toggle_tts)
        self.btn_tts_resumen.pack(side="left", padx=(0, 10))

        self.btn_word = ctk.CTkButton(f_btn_row, text=t("btn_word"), height=42, width=180,
                                     fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
                                     font=("Segoe UI", 13, "bold"),
                                     command=self.exportar_word)
        self.btn_word.pack(side="right")

    def _set_modelo(self, modelo):
        self.modelo_actual = modelo
        if modelo == "gemini":
            self.btn_gemini.configure(fg_color=COLOR_ACCENT_PRIMARY)
            self.btn_groq.configure(fg_color="transparent")
        else:
            self.btn_groq.configure(fg_color=COLOR_ACCENT_PURPLE)
            self.btn_gemini.configure(fg_color="transparent")

    def _actualizar_conteo(self, event=None):
        txt = self.txt_input.get("1.0", "end-1c")
        chars = len(txt)
        words = len(txt.split()) if txt.strip() else 0
        self.lbl_conteo_caracteres.configure(text=f"{words} palabras • {chars} caracteres")

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
        self.lbl_img_status.configure(text=f"{count} foto{'s' if count != 1 else ''}")

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

    def _extraer_texto_imagenes(self):
        if not self.imagenes_adjuntas:
            messagebox.showinfo("Sin imágenes", "Adjunta primero una o varias imágenes de apuntes o libros para extraer su texto.")
            return

        self.btn_extraer_ocr.configure(state="disabled")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        def _thread():
            try:
                prompt_ocr = (
                    "Transcribe y extrae fielmente TODO el texto, apuntes, definiciones, títulos, viñetas y fórmulas "
                    "visibles en las imágenes adjuntas. Mantén el orden lógico y no omitas detalles importantes. "
                    "Devuelve el texto extraído limpio y listo para su lectura y estudio."
                )
                texto_extraido = consultar_ia_multimodal(prompt_ocr, self.imagenes_adjuntas, modelo="gemini")
                
                def _actualizar():
                    actual = self.txt_input.get("1.0", "end-1c").strip()
                    if actual:
                        self.txt_input.insert("end", f"\n\n--- CONTENIDO EXTRAÍDO DE IMÁGENES ---\n\n{texto_extraido}")
                    else:
                        self.txt_input.insert("1.0", texto_extraido)
                    self._actualizar_conteo()
                    messagebox.showinfo("Texto Extraído", "Se ha transcrito el contenido de las imágenes en el cuadro de entrada.")

                self.after(0, _actualizar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error Visión OCR", f"No se pudo extraer el texto: {e}"))
            finally:
                self.after(0, lambda: [
                    self.progress_bar.stop(),
                    self.progress_bar.set(0),
                    self.btn_extraer_ocr.configure(state="normal")
                ])

        threading.Thread(target=_thread, daemon=True).start()

    def _copiar_salida(self):
        txt = self.txt_output.get("1.0", "end-1c").strip()
        if not txt:
            return
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo("Copiado", "Resumen copiado al portapapeles con éxito.")

    def _toggle_tts(self):
        if tts_engine.esta_reproduciendo():
            tts_engine.detener()
            self.btn_tts_resumen.configure(text=t("btn_escuchar"), fg_color=COLOR_BG_CARD)
        else:
            texto = self.txt_output.get("1.0", "end-1c").strip()
            if not texto or "ERROR:" in texto:
                messagebox.showinfo("Sin resumen", "Primero genera un resumen para escucharlo en voz alta.")
                return

            def _cb(rep):
                if rep:
                    self.btn_tts_resumen.configure(text="⏹️ Detener", fg_color=COLOR_DANGER)
                else:
                    self.btn_tts_resumen.configure(text=t("btn_escuchar"), fg_color=COLOR_BG_CARD)

            tts_engine.hablar(texto, callback_estado=lambda r: self.after(0, lambda: _cb(r)))

    def iniciar_proceso(self):
        texto = self.txt_input.get("1.0", "end-1c").strip()
        num_imgs = len(self.imagenes_adjuntas)

        if not texto and num_imgs == 0:
            messagebox.showwarning("Atención", "Introduce el texto a resumir o adjunta imágenes de apuntes/libros.")
            return

        self.txt_output.delete("1.0", "end")
        self.btn_procesar.configure(state="disabled")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        threading.Thread(target=self._ejecutar_ia, args=(texto,), daemon=True).start()

    def _ejecutar_ia(self, texto):
        try:
            titulo_tema = self.entry_nombre.get().strip()
            extra_info = f"TEMA/MATERIA: {titulo_tema}\n" if titulo_tema else ""

            if self.imagenes_adjuntas:
                full_prompt = (
                    f"{self.instrucciones}\n\n{extra_info}"
                    "Analiza minuciosamente las imágenes adjuntas (apuntes, fotos de páginas, esquemas o diapositivas) "
                    "y elabora un RESUMEN ACADÉMICO ESTRUCTURADO Y EXHAUSTIVO basado en todo su contenido."
                )
                if texto:
                    full_prompt += f"\n\nTexto adicional / notas del usuario:\n{texto}"
                resultado = consultar_ia_multimodal(full_prompt, self.imagenes_adjuntas, modelo="gemini")
            else:
                full_prompt = f"{self.instrucciones}\n\n{extra_info}Resume y desarrolla extensamente el siguiente texto:\n\n{texto}"
                if self.modelo_actual == "gemini":
                    resultado = llamar_gemini(full_prompt)
                else:
                    resultado = llamar_groq(full_prompt)

            self.after(0, self._escribir_output, resultado)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error al Resumir", f"Fallo al conectar con la IA: {e}"))
        finally:
            self.after(0, self._finalizar)

    def _escribir_output(self, texto):
        self.txt_output.insert("end", texto)
        self.txt_output.see("end")

    def _finalizar(self):
        self.progress_bar.stop()
        self.progress_bar.set(1)
        self.btn_procesar.configure(state="normal")

    def exportar_word(self):
        contenido = self.txt_output.get("1.0", "end-1c").strip()
        if not contenido or "ERROR:" in contenido:
            messagebox.showwarning("No se puede guardar", "No hay un resumen válido para exportar.")
            return

        nombre = self.entry_nombre.get().strip() or "Resumen_Academico"
        ruta = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Documento Word", "*.docx"), ("Todos los archivos", "*.*")],
            initialfile=f"Resumen_{nombre.replace(' ', '_')}.docx"
        )
        if ruta:
            try:
                doc = Document()
                title_p = doc.add_heading(f'Resumen Académico: {nombre}', 0)
                title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

                # Desglose de párrafos
                for line in contenido.split("\n"):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    if line_str.startswith("# ") or (line_str.isupper() and len(line_str) < 50):
                        doc.add_heading(line_str.replace("#", "").strip(), level=1)
                    elif line_str.startswith("## ") or line_str.startswith("1.") or line_str.startswith("2.") or line_str.startswith("3.") or line_str.startswith("4.") or line_str.startswith("5."):
                        doc.add_heading(line_str.replace("##", "").strip(), level=2)
                    elif line_str.startswith("•") or line_str.startswith("-") or line_str.startswith("*"):
                        p_b = doc.add_paragraph(style="List Bullet")
                        p_b.add_run(line_str.lstrip("•-* "))
                    else:
                        doc.add_paragraph(line_str)

                doc.save(ruta)
                messagebox.showinfo("Éxito", f"Documento Word guardado correctamente en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo Word: {e}")
