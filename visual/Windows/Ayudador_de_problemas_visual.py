import customtkinter as ctk
from tkinter import messagebox, filedialog
from openai import OpenAI
from docx import Document
import threading
import os
import json
from datetime import datetime

# Configuración visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SolucionadorIA(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Problem Solver - Alto Rendimiento Cloud")
        self.geometry("1000x700")

        # ───── CONFIGURACIÓN DEL CLIENTE GROQ ─────
        # RECUERDA: Tus amigos solo necesitan internet, la clave ya va integrada dentro de la app (.app)
        self.cliente_groq = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key="Your API KEY"  # <--- Pega aquí tu gsk_... de console.groq.com
        )

        # Variables de lógica
        self.historial_conversacion = []
        self.instrucciones = (
            "Eres un Solucionador de Problemas de alto rendimiento. "
            "Tu enfoque es: Analizar el problema -> Identificar la causa -> Dar solución técnica/práctica. -> Dar consejos para evitarlo en el futuro. "
            "Responde siempre con estructura de puntos clave y da conversación para acompañar y dar consejos."
        )

        # Persistencia del Historial de Chats
        self.ruta_historial = os.path.expanduser("~/.historial_solver.json")
        self.chat_actual_id = None
        self.todo_el_historial = self.cargar_historial_persistente()

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ───── PANEL LATERAL ─────
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="🛠️ Solver IA", font=("Segoe UI", 24, "bold")).pack(pady=20)

        self.entry_nombre = ctk.CTkEntry(self.sidebar, placeholder_text="¿Cuál es tu nombre?")
        self.entry_nombre.pack(fill="x", padx=20, pady=10)

        self.btn_exportar = ctk.CTkButton(self.sidebar, text="Exportar a Word",
                                          fg_color="#2c3e50", hover_color="#34495e",
                                          command=self.exportar_a_word)
        self.btn_exportar.pack(fill="x", padx=20, pady=10)

        self.btn_limpiar = ctk.CTkButton(self.sidebar, text="🧹 Limpiar Chat",
                                         fg_color="transparent", border_width=1,
                                         command=self.limpiar_chat)
        self.btn_limpiar.pack(fill="x", padx=20, pady=10)

        # ── SECCIÓN VISUAL DEL HISTORIAL ──
        ctk.CTkLabel(self.sidebar, text="🕒 Historial de Chats", font=("Segoe UI", 13, "bold")).pack(pady=(20, 5))
        self.frame_historial = ctk.CTkScrollableFrame(self.sidebar, height=220, fg_color="transparent")
        self.frame_historial.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(self.sidebar, text="Motor de IA:", font=("Segoe UI", 12)).pack(side="bottom", pady=5)
        self.status_label = ctk.CTkLabel(self.sidebar, text="🟢 Groq Cloud Listo", text_color="green")
        self.status_label.pack(side="bottom", pady=(0, 20))

        # Cargar los botones del historial al iniciar
        self.actualizar_ui_historial()

        # ───── ÁREA DE CHAT ─────
        self.chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.txt_chat = ctk.CTkTextbox(self.chat_frame, font=("Segoe UI", 14), state="disabled", wrap="word")
        self.txt_chat.grid(row=0, column=0, sticky="nsew", pady=(0, 15))

        # Entrada de usuario
        self.input_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry_pregunta = ctk.CTkEntry(self.input_frame, placeholder_text="Describe el problema aquí...", height=40)
        self.entry_pregunta.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_pregunta.bind("<Return>", lambda e: self.enviar_consulta())

        self.btn_enviar = ctk.CTkButton(self.input_frame, text="Analizar", width=120, height=40,
                                        command=self.enviar_consulta)
        self.btn_enviar.grid(row=0, column=1)

    # ───── LÓGICA DE INTERACCIÓN ─────

    def agregar_texto(self, emisor, texto):
        self.txt_chat.configure(state="normal")
        if emisor == "IA":
            self.txt_chat.insert("end", f"\n IA:\n{texto}")
        else:
            self.txt_chat.insert("end", f"\n\n {emisor}:\n{texto}\n")
        self.txt_chat.configure(state="disabled")
        self.txt_chat.see("end")

    def enviar_consulta(self):
        pregunta = self.entry_pregunta.get().strip()
        nombre = self.entry_nombre.get().strip() or "Tú"

        if not pregunta:
            return

        self.agregar_texto(nombre, pregunta)
        self.entry_pregunta.delete(0, "end")
        self.status_label.configure(text="🟡 Pensando (Groq)...", text_color="orange")

        # Guardar en memoria (formato compatible con OpenAI/Groq)
        self.historial_conversacion.append({'role': 'user', 'content': pregunta})

        # Lanzar hilo para no congelar la UI de CustomTkinter
        threading.Thread(target=self.proceso_ia, daemon=True).start()

    def proceso_ia(self):
        try:
            # CORRECCIÓN AQUÍ: Insertar el encabezado de IA de forma segura usando el hilo principal
            self.after(0, lambda: self.stream_update("\n IA:\n"))

            # Llamada exacta a la API Cloud de Groq utilizando streaming
            response = self.cliente_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{'role': 'system', 'content': self.instrucciones}] + self.historial_conversacion,
                stream=True,
                temperature=0.2
            )

            respuesta_completa = ""
            for chunk in response:
                # Comprobar que el fragmento de texto tiene contenido
                if chunk.choices[0].delta.content:
                    contenido = chunk.choices[0].delta.content
                    respuesta_completa += contenido
                    # Actualizar texto en la UI de CustomTkinter de forma segura
                    self.after(0, self.stream_update, contenido)

            self.historial_conversacion.append({'role': 'assistant', 'content': respuesta_completa})

            # Guardar automáticamente la sesión en el historial al terminar la respuesta
            self.guardar_en_historial()

            self.after(0, lambda: self.status_label.configure(text="🟢 Groq Cloud Listo", text_color="green"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Fallo de conexión Cloud: {str(e)}"))
            self.after(0, lambda: self.status_label.configure(text="🔴 Error de red", text_color="red"))
        finally:
            self.after(0, lambda: self.txt_chat.configure(state="disabled"))

    def stream_update(self, contenido):
        self.txt_chat.configure(state="normal")
        self.txt_chat.insert("end", contenido)
        self.txt_chat.see("end")
        self.txt_chat.configure(state="disabled")

    def limpiar_chat(self):
        self.txt_chat.configure(state="normal")
        self.txt_chat.delete("1.0", "end")
        self.txt_chat.configure(state="disabled")
        self.historial_conversacion = []
        self.chat_actual_id = None

    def exportar_a_word(self):
        if not self.historial_conversacion:
            messagebox.showwarning("Atención", "No hay nada que exportar aún.")
            return

        nombre = self.entry_nombre.get().strip() or "Usuario"
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"Solucion_Problemas_{nombre}.docx",
            title="Guardar informe técnico"
        )

        if path:
            try:
                doc = Document()
                doc.add_heading(f'Informe de Solución - {nombre}', 0)

                for msg in self.historial_conversacion:
                    rol = "Tú" if msg['role'] == 'user' else "IA"
                    p = doc.add_paragraph()
                    p.add_run(f"{rol}: ").bold = True
                    p.add_run(msg['content'])

                doc.save(path)
                messagebox.showinfo("Éxito", f"Informe guardado en:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    # ───── LÓGICA EXTRA DEL HISTORIAL PERSISTENTE ─────

    def cargar_historial_persistente(self):
        if os.path.exists(self.ruta_historial):
            try:
                with open(self.ruta_historial, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def guardar_en_historial(self):
        if not self.historial_conversacion:
            return

        # Si es un chat nuevo, generamos un identificador con hora y las primeras palabras
        if self.chat_actual_id is None:
            primer_msg = next((m['content'] for m in self.historial_conversacion if m['role'] == 'user'),
                              "Conversación")
            resumen = primer_msg[:22] + "..." if len(primer_msg) > 22 else primer_msg
            hora = datetime.now().strftime("%H:%M")
            self.chat_actual_id = f"[{hora}] {resumen}"

        self.todo_el_historial[self.chat_actual_id] = self.historial_conversacion

        try:
            with open(self.ruta_historial, 'w', encoding='utf-8') as f:
                json.dump(self.todo_el_historial, f, ensure_ascii=False, indent=2)
            self.after(0, self.actualizar_ui_historial)
        except Exception as e:
            print(f"Error al guardar historial: {e}")

    def actualizar_ui_historial(self):
        """Dibuja dinámicamente las filas del historial con un botón para abrirlo y un botón ❌ al lado."""
        # Limpiar los botones antiguos del contenedor con scroll
        for widget in self.frame_historial.winfo_children():
            widget.destroy()

        # Re-dibujar botones en orden inverso (el más reciente arriba)
        for chat_id in reversed(list(self.todo_el_historial.keys())):
            # Mini frame contenedor horizontal para agrupar los dos botones
            frame_fila = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
            frame_fila.pack(fill="x", pady=4, padx=2)

            # BOTÓN PRINCIPAL: Carga y abre la conversación del historial
            btn = ctk.CTkButton(
                frame_fila,
                text=chat_id,
                fg_color="transparent",
                text_color="#dcdde1",
                anchor="w",
                hover_color="#34495e",
                height=35,
                command=lambda cid=chat_id: self.cargar_conversacion_del_historial(cid)
            )
            btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

            # BOTÓN DE BORRAR (❌): Elimina permanentemente esta conversación concreta
            btn_borrar = ctk.CTkButton(
                frame_fila,
                text="❌",
                width=35,
                height=35,
                fg_color="#A30000",  # Rojo oscuro
                hover_color="#7A0000",  # Rojo oscuro intenso al pasar el ratón
                command=lambda cid=chat_id: self.eliminar_chat_directo(cid)
            )
            btn_borrar.pack(side="right")

    def eliminar_chat_directo(self, chat_id):
        """Elimina permanentemente una conversación desde el botón ❌."""
        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas borrar este chat del historial?\n\n'{chat_id}'"):

            # 1. Eliminar del diccionario en memoria
            if chat_id in self.todo_el_historial:
                del self.todo_el_historial[chat_id]

            # 2. Persistir los cambios en el archivo JSON externo
            try:
                with open(self.ruta_historial, 'w', encoding='utf-8') as f:
                    json.dump(self.todo_el_historial, f, ensure_ascii=False, indent=2)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el historial actualizado: {e}")

            # 3. Si estabas visualizando el chat que acabas de borrar, limpia la pantalla
            if self.chat_actual_id == chat_id:
                self.limpiar_chat()

            # 4. Refrescar visualmente la lista lateral inmediatamente
            self.actualizar_ui_historial()
            messagebox.showinfo("Éxito", "Conversación eliminada del historial.")

    def cargar_conversacion_del_historial(self, chat_id):
        self.chat_actual_id = chat_id
        self.historial_conversacion = self.todo_el_historial[chat_id]

        self.txt_chat.configure(state="normal")
        self.txt_chat.delete("1.0", "end")

        # Re-dibujar el chat completo respetando de forma exacta los formatos de emisor de tu app
        for msg in self.historial_conversacion:
            if msg['role'] == 'user':
                nombre = self.entry_nombre.get().strip() or "Tú"
                self.txt_chat.insert("end", f"\n\n {nombre}:\n{msg['content']}\n")
            elif msg['role'] == 'assistant':
                self.txt_chat.insert("end", f"\n IA:\n{msg['content']}")

        self.txt_chat.configure(state="disabled")
        self.txt_chat.see("end")


if __name__ == "__main__":
    app = SolucionadorIA()
    app.mainloop()