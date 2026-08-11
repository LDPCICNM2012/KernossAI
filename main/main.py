# ══════════════════════════════════════════════════════════════════════════════
#  sAI  —  main.py  (MONOLÍTICO, sin subprocesos)
#  Todos los módulos están integrados aquí directamente.
# ══════════════════════════════════════════════════════════════════════════════

import matplotlib
matplotlib.use("TkAgg")

import sys
import os
import json
import hashlib
import re
import threading
import calendar
from datetime import datetime
import requests

import customtkinter as ctk
from tkinter import messagebox, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from auth_backend import login, registro, llamar_gemini, llamar_groq, token_guardado, borrar_token

# ─────────────────────────────────────────────
#  CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

RUTA_SESION    = os.path.expanduser("~/.immune_session.json")
RUTA_USUARIOS  = os.path.expanduser("~/.immune_usuarios.json")




def construir_prompt(instrucciones, historial=None):
    partes = [instrucciones.strip()]
    if historial:
        for msg in historial:
            rol = "IA" if msg.get("role") == "assistant" else msg.get("role", "Usuario").capitalize()
            partes.append(f"{rol}: {msg.get('content', '')}")
    return "\n\n".join(partes)

# ─────────────────────────────────────────────
#  UTILIDADES DE SESIÓN
# ─────────────────────────────────────────────
def cargar_sesion():
    if os.path.exists(RUTA_SESION):
        try:
            with open(RUTA_SESION, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def guardar_sesion(datos):
    with open(RUTA_SESION, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def cerrar_sesion():
    if os.path.exists(RUTA_SESION):
        os.remove(RUTA_SESION)

def cargar_usuarios():
    if os.path.exists(RUTA_USUARIOS):
        try:
            with open(RUTA_USUARIOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_usuarios(usuarios):
    with open(RUTA_USUARIOS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA DE LOGIN / REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
class PantallaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kernosss AI – Acceso")
        self.geometry("520x640")
        self.resizable(False, False)
        self.usuario_autenticado = None
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Kernosss\nAI",
                     font=("Segoe UI", 36, "bold"), text_color="#1f6aa5").pack(pady=(50, 5))
        ctk.CTkLabel(self, text="2026 Edition",
                     font=("Segoe UI", 14), text_color="#888").pack(pady=(0, 40))

        self.frame = ctk.CTkFrame(self, corner_radius=16, fg_color="#1a1a2e")
        self.frame.pack(padx=50, fill="x")

        self.tab = ctk.CTkTabview(self.frame, height=320)
        self.tab.pack(fill="x", padx=20, pady=20)
        self.tab.add("Iniciar Sesión")
        self.tab.add("Registrarse")

        # ── LOGIN ──
        login = self.tab.tab("Iniciar Sesión")
        ctk.CTkLabel(login, text="Correo electrónico", anchor="w").pack(fill="x", padx=10, pady=(10, 2))
        self.entry_login_email = ctk.CTkEntry(login, placeholder_text="tu@correo.com", height=38)
        self.entry_login_email.pack(fill="x", padx=10)
        ctk.CTkLabel(login, text="Contraseña", anchor="w").pack(fill="x", padx=10, pady=(10, 2))
        self.entry_login_pass = ctk.CTkEntry(login, placeholder_text="••••••••", show="•", height=38)
        self.entry_login_pass.pack(fill="x", padx=10)
        self.entry_login_pass.bind("<Return>", lambda e: self._login())
        ctk.CTkButton(login, text="Iniciar Sesión", height=40,
                      command=self._login).pack(fill="x", padx=10, pady=(20, 5))
        self.lbl_login_error = ctk.CTkLabel(login, text="", text_color="red", font=("Segoe UI", 11))
        self.lbl_login_error.pack()

        # ── REGISTRO ──
        reg = self.tab.tab("Registrarse")
        ctk.CTkLabel(reg, text="Nombre completo", anchor="w").pack(fill="x", padx=10, pady=(10, 2))
        self.entry_reg_nombre = ctk.CTkEntry(reg, placeholder_text="Tu nombre", height=38)
        self.entry_reg_nombre.pack(fill="x", padx=10)
        ctk.CTkLabel(reg, text="Correo electrónico", anchor="w").pack(fill="x", padx=10, pady=(8, 2))
        self.entry_reg_email = ctk.CTkEntry(reg, placeholder_text="tu@correo.com", height=38)
        self.entry_reg_email.pack(fill="x", padx=10)
        ctk.CTkLabel(reg, text="Contraseña", anchor="w").pack(fill="x", padx=10, pady=(8, 2))
        self.entry_reg_pass = ctk.CTkEntry(reg, placeholder_text="Mínimo 6 caracteres", show="•", height=38)
        self.entry_reg_pass.pack(fill="x", padx=10)
        ctk.CTkLabel(reg, text="Rol", anchor="w").pack(fill="x", padx=10, pady=(8, 2))
        self.combo_rol = ctk.CTkOptionMenu(reg, values=["Alumno", "Profesor"], height=38)
        self.combo_rol.pack(fill="x", padx=10)
        ctk.CTkButton(reg, text="Crear Cuenta", height=40,
                      command=self._registrar).pack(fill="x", padx=10, pady=(15, 5))
        self.lbl_reg_error = ctk.CTkLabel(reg, text="", text_color="red", font=("Segoe UI", 11))
        self.lbl_reg_error.pack()

        ctk.CTkLabel(self, text="Tus datos se guardan localmente en tu dispositivo.",
                     font=("Segoe UI", 10), text_color="#555").pack(pady=(20, 0))

    def _login(self):
        email    = self.entry_login_email.get().strip().lower()
        password = self.entry_login_pass.get()
        if not email or not password:
            self.lbl_login_error.configure(text="Completa todos los campos.")
            return
        usuarios = cargar_usuarios()
        if email not in usuarios:
            self.lbl_login_error.configure(text="Correo no registrado.")
            return
        if usuarios[email]["password"] != hash_password(password):
            self.lbl_login_error.configure(text="Contraseña incorrecta.")
            return
        sesion = {"email": email, "nombre": usuarios[email]["nombre"], "rol": usuarios[email]["rol"]}
        guardar_sesion(sesion)
        self.usuario_autenticado = sesion
        self.destroy()

    def _registrar(self):
        nombre   = self.entry_reg_nombre.get().strip()
        email    = self.entry_reg_email.get().strip().lower()
        password = self.entry_reg_pass.get()
        rol      = self.combo_rol.get()
        if not nombre or not email or not password:
            self.lbl_reg_error.configure(text="Completa todos los campos.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.lbl_reg_error.configure(text="Correo inválido.")
            return
        if len(password) < 6:
            self.lbl_reg_error.configure(text="La contraseña debe tener al menos 6 caracteres.")
            return
        usuarios = cargar_usuarios()
        if email in usuarios:
            self.lbl_reg_error.configure(text="Este correo ya está registrado.")
            return
        usuarios[email] = {"nombre": nombre, "password": hash_password(password), "rol": rol}
        guardar_usuarios(usuarios)
        sesion = {"email": email, "nombre": nombre, "rol": rol}
        guardar_sesion(sesion)
        self.usuario_autenticado = sesion
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: CALCULADOR DE MEDIAS
# ══════════════════════════════════════════════════════════════════════════════
class ModuloCalculador(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.notas_finales  = []
        self.nombres_notas  = []
        self.porcentajes    = []
        self.canvas_grafico = None
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.pack(fill="x", padx=20, pady=(20, 15))
        ctk.CTkLabel(frame_titulo, text="Calculadora de Medias",
                     font=("Segoe UI", 32, "bold"),
                     text_color=["#0d47a1", "#64b5f6"]).pack()
        ctk.CTkLabel(frame_titulo, text="Organiza y calcula el promedio de tus calificaciones",
                     font=("Segoe UI", 12),
                     text_color=["#424242", "#bdbdbd"]).pack(pady=(3, 0))

        self.frame_entrada = ctk.CTkFrame(self, corner_radius=12, border_width=1,
                                          border_color=["#e0e0e0", "#333333"])
        self.frame_entrada.pack(padx=25, pady=15, fill="both", expand=False)
        self.frame_entrada.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.frame_entrada, text="Materia o Asignatura",
                     font=("Segoe UI", 13, "bold")).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.entrada_nombre = ctk.CTkEntry(self.frame_entrada, placeholder_text="Ej: Matemáticas, Física...",
                                           height=40, font=("Segoe UI", 12))
        self.entrada_nombre.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(self.frame_entrada, text="Nota Directa",
                     font=("Segoe UI", 13, "bold")).grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")
        self.entrada_nota_directa = ctk.CTkEntry(self.frame_entrada, placeholder_text="Ej: 9.5",
                                                  height=40, font=("Segoe UI", 12))
        self.entrada_nota_directa.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(self.frame_entrada,
                     text="% del Total (según criterios: 60% Pruebas / 30% Proyectos / 10% Observación)",
                     font=("Segoe UI", 13, "bold")).grid(row=2, column=0, padx=15, pady=(0, 5), sticky="w")
        self.entrada_porcentaje = ctk.CTkEntry(self.frame_entrada,
                                               placeholder_text="Ej: 60 (Pruebas) / 30 (Proyectos) / 10 (Observación)",
                                               height=40, font=("Segoe UI", 12))
        self.entrada_porcentaje.grid(row=3, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")

        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(fill="x", padx=25, pady=12)
        frame_botones.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(frame_botones, text="Guardar Nota",
                      command=self.agregar_nota_principal,
                      fg_color="#4caf50", hover_color="#388e3c",
                      height=40, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(frame_botones, text="Agregar Subnotas",
                      command=self.gestionar_subnotas,
                      fg_color="transparent", border_width=2,
                      border_color=["#0288d1", "#4dd0e1"],
                      height=40, font=("Segoe UI", 12, "bold")).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.pack(padx=25, pady=15, fill="both", expand=True)
        frame_principal.grid_columnconfigure((0, 1), weight=1)
        frame_principal.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame_principal, text="Registro de Notas",
                     font=("Segoe UI", 16, "bold")).grid(row=0, column=0, pady=(0, 8), padx=(0, 10), sticky="w")
        self.salida_texto = ctk.CTkTextbox(frame_principal, width=500, height=350,
                                           font=("Courier New", 11), corner_radius=10,
                                           border_width=1, state="disabled")
        self.salida_texto.grid(row=1, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(frame_principal, text="Visualización de Notas",
                     font=("Segoe UI", 16, "bold")).grid(row=0, column=1, pady=(0, 8), padx=(10, 0), sticky="w")
        self.frame_grafico = ctk.CTkFrame(frame_principal, corner_radius=10, border_width=1)
        self.frame_grafico.grid(row=1, column=1, padx=(10, 0), sticky="nsew")

        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.pack(padx=25, pady=15, fill="x")
        frame_acciones.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(frame_acciones, text="Calcular Promedio Final",
                      command=self.calcular_total_final,
                      height=45, font=("Segoe UI", 12, "bold"),
                      fg_color="#0277bd", hover_color="#01579b").grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(frame_acciones, text="Limpiar Todo",
                      command=self.limpiar_datos,
                      fg_color="#ff9800", hover_color="#f57c00",
                      height=45, font=("Segoe UI", 12, "bold")).grid(row=0, column=1, padx=3, sticky="ew")
        ctk.CTkButton(frame_acciones, text="Exportar a Word",
                      command=self.exportar_a_word,
                      fg_color="#7c3aed", hover_color="#5b21b6",
                      height=45, font=("Segoe UI", 12, "bold")).grid(row=0, column=2, padx=(6, 0), sticky="ew")

    def calcular_media(self, lista):
        if not lista:
            return 0
        return sum(lista) / len(lista)

    def actualizar_grafico(self):
        if not self.notas_finales:
            return
        if self.canvas_grafico:
            self.canvas_grafico.get_tk_widget().destroy()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.patch.set_facecolor('#1a1a1a')
        colores = ['#4caf50' if n >= 7 else '#ff9800' if n >= 5 else '#f44336' for n in self.notas_finales]
        ax1.bar(range(len(self.nombres_notas)), self.notas_finales, color=colores, alpha=0.8, edgecolor='white')
        ax1.set_xticks(range(len(self.nombres_notas)))
        ax1.set_xticklabels(self.nombres_notas, rotation=45, ha='right', fontsize=9)
        ax1.set_ylabel('Calificación', color='white', fontsize=10)
        ax1.set_title('Notas por Asignatura', color='white', fontsize=12, fontweight='bold')
        ax1.set_ylim(0, 10)
        ax1.set_facecolor('#2a2a2a')
        ax1.tick_params(colors='white')
        ax1.grid(axis='y', alpha=0.3, color='white')
        promedio = self.calcular_media(self.notas_finales)
        por_encima = sum(1 for n in self.notas_finales if n >= promedio)
        por_debajo = sum(1 for n in self.notas_finales if n < promedio)
        ax2.pie([max(por_encima, 0.001), max(por_debajo, 0.001)],
                labels=[f'Arriba del promedio\n({por_encima})', f'Debajo del promedio\n({por_debajo})'],
                colors=['#4caf50', '#f44336'], autopct='%1.1f%%', startangle=90,
                textprops={'color': 'white', 'fontsize': 10})
        ax2.set_title(f'Distribución (Promedio: {promedio:.2f})', color='white', fontsize=12, fontweight='bold')
        plt.tight_layout()
        self.canvas_grafico = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        self.canvas_grafico.draw()
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True)

    def gestionar_subnotas(self):
        nombre_principal = self.entrada_nombre.get().strip()
        if not nombre_principal:
            messagebox.showwarning("Atención", "Escribe el nombre de la asignatura primero.")
            return
        d = ctk.CTkInputDialog(text=f"¿Cuántos bloques tiene {nombre_principal}?\n(Ej: 3 → Exámenes, Clase, Deberes)",
                               title="Bloques de calificación")
        res = d.get_input()
        self.focus_force(); self.lift()
        if not res or not res.isdigit():
            return
        num_bloques = int(res)
        self.salida_texto.configure(state="normal")
        self.salida_texto.insert("end", f"\n{'─'*60}\n  📚 {nombre_principal.upper()}\n{'─'*60}\n")
        nota_final_asignatura = 0.0
        suma_pesos_bloques = 0.0
        for i in range(num_bloques):
            d = ctk.CTkInputDialog(text=f"Nombre del bloque {i+1}:", title="Nombre del bloque")
            nombre_bloque = d.get_input(); self.focus_force(); self.lift()
            if nombre_bloque is None: break
            d = ctk.CTkInputDialog(text=f"¿Cuánto vale '{nombre_bloque}' en % sobre el total?", title="% del bloque")
            peso_bloque_str = d.get_input(); self.focus_force(); self.lift()
            if peso_bloque_str is None: break
            try:
                peso_bloque = float(peso_bloque_str)
            except ValueError:
                messagebox.showerror("Error", "Número inválido."); continue
            d = ctk.CTkInputDialog(text=f"¿Cuántas notas hay dentro de '{nombre_bloque}'?", title="Notas del bloque")
            res_sub = d.get_input(); self.focus_force(); self.lift()
            if not res_sub or not res_sub.isdigit(): continue
            num_sub = int(res_sub)
            self.salida_texto.insert("end", f"\n  📂 {nombre_bloque} ({peso_bloque:.0f}% del total)\n")
            nota_bloque_ponderada = 0.0; suma_pesos_sub = 0.0
            for j in range(num_sub):
                d = ctk.CTkInputDialog(text=f"Nombre de la nota {j+1}:", title="Nota")
                nombre_sub = d.get_input(); self.focus_force(); self.lift()
                if nombre_sub is None: break
                d = ctk.CTkInputDialog(text=f"¿Cuánto vale '{nombre_sub}' en % dentro de '{nombre_bloque}'?", title=f"% dentro de {nombre_bloque}")
                peso_sub_str = d.get_input(); self.focus_force(); self.lift()
                if peso_sub_str is None: break
                try:
                    peso_sub = float(peso_sub_str)
                except ValueError:
                    messagebox.showerror("Error", "Número inválido."); continue
                d = ctk.CTkInputDialog(text=f"Calificación de '{nombre_sub}':", title="Calificación")
                valor_sub_str = d.get_input(); self.focus_force(); self.lift()
                if valor_sub_str is None: break
                try:
                    valor_sub = float(valor_sub_str)
                except ValueError:
                    messagebox.showerror("Error", "Número inválido."); continue
                nota_bloque_ponderada += valor_sub * (peso_sub / 100)
                suma_pesos_sub += peso_sub
                self.salida_texto.insert("end", f"      • {nombre_sub:20} {peso_sub:.0f}% → {valor_sub:.2f}\n")
            if suma_pesos_sub > 0 and suma_pesos_sub != 100:
                nota_bloque_ponderada = nota_bloque_ponderada / (suma_pesos_sub / 100)
            self.salida_texto.insert("end", f"    ✓ Nota del bloque '{nombre_bloque}': {nota_bloque_ponderada:.2f}\n")
            nota_final_asignatura += nota_bloque_ponderada * (peso_bloque / 100)
            suma_pesos_bloques += peso_bloque
        if suma_pesos_bloques > 0 and suma_pesos_bloques != 100:
            nota_final_asignatura = nota_final_asignatura / (suma_pesos_bloques / 100)
        self.nombres_notas.append(nombre_principal)
        self.notas_finales.append(nota_final_asignatura)
        self.porcentajes.append(100.0)
        self.salida_texto.insert("end", f"\n  {'═'*50}\n  ✅ NOTA FINAL {nombre_principal.upper()}: {nota_final_asignatura:.2f}\n  {'═'*50}\n\n")
        self.salida_texto.configure(state="disabled")
        self.entrada_nombre.delete(0, "end")
        self.actualizar_grafico()

    def agregar_nota_principal(self):
        nombre = self.entrada_nombre.get().strip()
        nota_str = self.entrada_nota_directa.get().strip()
        porcentaje_str = self.entrada_porcentaje.get().strip()
        if nombre and nota_str:
            try:
                nota = float(nota_str)
                if porcentaje_str:
                    porcentaje_sobre_total = float(porcentaje_str)
                else:
                    total = len(self.notas_finales) + 1
                    porcentaje_sobre_total = (1 / total) * 100
                self.nombres_notas.append(nombre)
                self.notas_finales.append(nota)
                self.porcentajes.append(porcentaje_sobre_total)
                self.salida_texto.configure(state="normal")
                self.salida_texto.insert("end", f"  ✓ {nombre:25} → {nota:.2f} ({porcentaje_sobre_total:.1f}%)\n")
                self.salida_texto.configure(state="disabled")
                self.entrada_nombre.delete(0, "end")
                self.entrada_nota_directa.delete(0, "end")
                self.entrada_porcentaje.delete(0, "end")
                self.actualizar_grafico()
            except ValueError:
                messagebox.showerror("Error", "La calificación y el porcentaje deben ser números válidos.")
        else:
            messagebox.showwarning("Campos incompletos", "Por favor completa materia y calificación.")

    def calcular_total_final(self):
        if not self.notas_finales:
            messagebox.showinfo("Sin datos", "No hay calificaciones guardadas para calcular.")
            return
        suma_ponderada = sum(n * (p / 100) for n, p in zip(self.notas_finales, self.porcentajes))
        total_porcentaje = sum(self.porcentajes)
        media_total = suma_ponderada / (total_porcentaje / 100) if total_porcentaje != 100 else suma_ponderada
        self.salida_texto.configure(state="normal")
        self.salida_texto.insert("end", f"\n{'═'*60}\n  📊 RESULTADO FINAL\n")
        self.salida_texto.insert("end", f"  Asignaturas: {len(self.nombres_notas)}\n")
        self.salida_texto.insert("end", f"  Peso total asignado: {total_porcentaje:.1f}%\n")
        self.salida_texto.insert("end", f"  Promedio Ponderado: {media_total:.2f}\n{'═'*60}\n\n")
        self.salida_texto.configure(state="disabled")
        self.salida_texto.see("end")

    def limpiar_datos(self):
        if messagebox.askyesno("Confirmar", "¿Deseas limpiar todas las notas?"):
            self.notas_finales.clear(); self.nombres_notas.clear(); self.porcentajes.clear()
            self.salida_texto.configure(state="normal")
            self.salida_texto.delete("1.0", "end")
            self.salida_texto.configure(state="disabled")
            self.entrada_nombre.delete(0, "end")
            self.entrada_nota_directa.delete(0, "end")
            self.entrada_porcentaje.delete(0, "end")
            if self.canvas_grafico:
                self.canvas_grafico.get_tk_widget().destroy()
                self.canvas_grafico = None

    def exportar_a_word(self):
        if not self.notas_finales:
            messagebox.showwarning("Sin datos", "No hay calificaciones para exportar.")
            return
        doc = Document()
        titulo = doc.add_heading('Reporte de Calificaciones', 0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fecha = doc.add_paragraph(f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
        fecha.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
        tabla = doc.add_table(rows=len(self.nombres_notas) + 1, cols=3)
        tabla.style = 'Light Grid Accent 1'
        enc = tabla.rows[0].cells
        enc[0].text = '#'; enc[1].text = 'Asignatura'; enc[2].text = 'Calificación'
        for i, (nombre, nota) in enumerate(zip(self.nombres_notas, self.notas_finales), start=1):
            fila = tabla.rows[i].cells
            fila[0].text = str(i); fila[1].text = nombre; fila[2].text = f"{nota:.2f}"
        doc.add_paragraph()
        promedio = self.calcular_media(self.notas_finales)
        p = doc.add_paragraph(f'Promedio General: {promedio:.2f}')
        p.runs[0].font.bold = True; p.runs[0].font.size = Pt(14)
        ruta = os.path.join(os.path.expanduser("~/Documents"),
                            f"Reporte_Calificaciones_{datetime.now().strftime('%d%m%Y_%H%M%S')}.docx")
        doc.save(ruta)
        messagebox.showinfo("Éxito", f"Documento exportado a:\n{ruta}")


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: APUNTADOR DE NOTAS
# ══════════════════════════════════════════════════════════════════════════════
class ModuloApuntador(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.archivo_actual = None
        self.notas_guardadas = {}
        self._cargar_notas()
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panel lateral
        self.frame_lateral = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.frame_lateral.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.frame_lateral, text="Mis Notas",
                     font=("Segoe UI", 20, "bold")).pack(pady=20, padx=10)
        self.entrada_nombre_nota = ctk.CTkEntry(self.frame_lateral, placeholder_text="Nueva nota...")
        self.entrada_nombre_nota.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.frame_lateral, text="Crear Nota",
                      command=self.crear_nueva_nota,
                      fg_color="#28a745", hover_color="#218838").pack(fill="x", padx=10, pady=5)
        self.lista_notas_frame = ctk.CTkScrollableFrame(self.frame_lateral, label_text="Notas Guardadas")
        self.lista_notas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Área de edición
        self.frame_editor = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_editor.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.frame_editor.grid_rowconfigure(1, weight=1)
        self.frame_editor.grid_columnconfigure(0, weight=1)
        self.label_nota_abierta = ctk.CTkLabel(self.frame_editor, text="Seleccione una nota",
                                               font=("Segoe UI", 16, "italic"))
        self.label_nota_abierta.grid(row=0, column=0, pady=(0, 10), sticky="w")
        self.editor_texto = ctk.CTkTextbox(self.frame_editor, font=("Consolas", 13), border_width=1)
        self.editor_texto.grid(row=1, column=0, sticky="nsew")
        frame_btns = ctk.CTkFrame(self.frame_editor, fg_color="transparent")
        frame_btns.grid(row=2, column=0, pady=(15, 0), sticky="ew")
        ctk.CTkButton(frame_btns, text="Guardar", command=self.guardar_nota).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Eliminar", fg_color="#dc3545", hover_color="#c82333",
                      command=self.eliminar_nota).pack(side="left", padx=5)
        ctk.CTkButton(frame_btns, text="Exportar Word",
                      command=self.exportar_nota_word).pack(side="right", padx=5)
        self.actualizar_listbox()

    def crear_nueva_nota(self):
        nombre = self.entrada_nombre_nota.get().strip()
        if nombre:
            if nombre not in self.notas_guardadas:
                self.notas_guardadas[nombre] = ""
                self._guardar_notas()
                self.abrir_nota(nombre)
                self.actualizar_listbox()
                self.entrada_nombre_nota.delete(0, "end")
            else:
                messagebox.showwarning("Error", "La nota ya existe.")

    def abrir_nota(self, nombre):
        self.archivo_actual = nombre
        self.label_nota_abierta.configure(text=f"Editando: {nombre}", font=("Segoe UI", 16, "bold"))
        self.editor_texto.delete("1.0", "end")
        self.editor_texto.insert("1.0", self.notas_guardadas[nombre])

    def actualizar_listbox(self):
        for w in self.lista_notas_frame.winfo_children():
            w.destroy()
        for nombre in self.notas_guardadas:
            ctk.CTkButton(self.lista_notas_frame, text=f"• {nombre}", anchor="w",
                          fg_color="transparent", text_color=("black", "white"),
                          hover_color=("#dbdbdb", "#2b2b2b"),
                          command=lambda n=nombre: self.abrir_nota(n)).pack(fill="x", pady=2)

    def guardar_nota(self):
        if self.archivo_actual:
            self.notas_guardadas[self.archivo_actual] = self.editor_texto.get("1.0", "end-1c")
            self._guardar_notas()
            messagebox.showinfo("Guardado", "Nota guardada correctamente.")

    def eliminar_nota(self):
        if self.archivo_actual and messagebox.askyesno("Confirmar", f"¿Eliminar '{self.archivo_actual}'?"):
            del self.notas_guardadas[self.archivo_actual]
            self._guardar_notas()
            self.archivo_actual = None
            self.editor_texto.delete("1.0", "end")
            self.label_nota_abierta.configure(text="Seleccione una nota")
            self.actualizar_listbox()

    def exportar_nota_word(self):
        if not self.archivo_actual:
            return
        doc = Document()
        doc.add_heading(self.archivo_actual, 0)
        doc.add_paragraph(self.editor_texto.get("1.0", "end-1c"))
        path = filedialog.asksaveasfilename(defaultextension=".docx",
                                            initialfile=f"{self.archivo_actual}.docx")
        if path:
            doc.save(path)
            messagebox.showinfo("Éxito", "Exportado correctamente.")

    def _guardar_notas(self):
        ruta = os.path.expanduser("~/.apuntador_notas.json")
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(self.notas_guardadas, f, ensure_ascii=False, indent=2)

    def _cargar_notas(self):
        ruta = os.path.expanduser("~/.apuntador_notas.json")
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                self.notas_guardadas = json.load(f)


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: RESUMIDOR DE TEXTOS AI
# ══════════════════════════════════════════════════════════════════════════════
class ModuloResumidor(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.modelo = "groq"
        self.instrucciones = (
            "Eres un experto en el tema proporcionado. Tu conocimiento se basa estrictamente en hechos reales. "
            "REGLA DE SEGURIDAD ABSOLUTA: Solo puedes responder a temas que pertenezcan al ámbito educativo, "
            "académico, histórico o laboral. Si el usuario te pide algo fuera de estos ámbitos, DEBES responder "
            "ÚNICAMENTE con la frase: 'ERROR: La petición no pertenece al ámbito educativo o laboral.' "
            "Si la petición es válida, redacta un texto muy extenso, preciso y con párrafos bien estructurados "
            "explicando el contexto, las causas y las consecuencias. No inventes datos bajo ninguna circunstancia."
        )
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(header, text="🎓 Resumidor De Textos AI",
                     font=("Segoe UI", 28, "bold")).pack(side="left")
        self.entry_nombre = ctk.CTkEntry(header, placeholder_text="Tu nombre...", width=200)
        self.entry_nombre.pack(side="right", padx=10)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, padx=20, sticky="nsew")
        main.grid_columnconfigure((0, 1), weight=1)
        main.grid_rowconfigure(0, weight=1)

        input_f = ctk.CTkFrame(main)
        input_f.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(input_f, text="Pega tus apuntes o tema aquí:", font=("Segoe UI", 13, "bold")).pack(pady=10)
        self.txt_input = ctk.CTkTextbox(input_f, font=("Segoe UI", 12))
        self.txt_input.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        output_f = ctk.CTkFrame(main)
        output_f.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(output_f, text="Resumen generado por IA:", font=("Segoe UI", 13, "bold")).pack(pady=10)
        self.txt_output = ctk.CTkTextbox(output_f, font=("Segoe UI", 13), fg_color=("#ebebeb", "#1a1a1a"))
        self.txt_output.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.progress_bar = ctk.CTkProgressBar(footer)
        self.progress_bar.pack(fill="x", pady=(0, 15))
        self.progress_bar.set(0)
        self.btn_procesar = ctk.CTkButton(footer, text="Generar Resumen Riguroso",
                                          height=45, font=("Segoe UI", 14, "bold"),
                                          command=self.iniciar_proceso)
        self.btn_procesar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(footer, text="Guardar en Word", height=45, width=200,
                      fg_color="#27ae60", hover_color="#219150",
                      command=self.exportar_word).pack(side="right")

    def iniciar_proceso(self):
        texto = self.txt_input.get("1.0", "end-1c").strip()
        if not texto:
            messagebox.showwarning("Atención", "Por favor, introduce el texto que deseas resumir.")
            return
        self.txt_output.delete("1.0", "end")
        self.btn_procesar.configure(state="disabled")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        threading.Thread(target=self._ejecutar_ia, args=(texto,), daemon=True).start()

    def _ejecutar_ia(self, texto):
        try:
            resultado = llamar_groq(
                f"{self.instrucciones}\n\nDesarrolla o resume de manera extensa y rigurosa: {texto}"
            )
            self.after(0, self._escribir_output, resultado)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Cloud", f"Fallo al conectar con IA: {e}"))
        finally:
            self.after(0, self._finalizar)

    def _escribir_output(self, char):
        self.txt_output.insert("end", char)
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
        nombre = self.entry_nombre.get().strip() or "Usuario"
        ruta = filedialog.asksaveasfilename(defaultextension=".docx",
                                            initialfile=f"Resumen_{nombre}.docx")
        if ruta:
            try:
                doc = Document()
                doc.add_heading(f'Resumen Académico de {nombre}', 0)
                doc.add_paragraph(contenido)
                doc.save(ruta)
                messagebox.showinfo("Éxito", f"Archivo guardado en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: GENERADOR DE EXÁMENES AI
# ══════════════════════════════════════════════════════════════════════════════
class ModuloExamen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.examen_en_memoria = ""
        self.historial_conversacion = []
        self.instrucciones_base = (
            "Eres un evaluador académico profesional. El examen debe tener:\n"
            "1. Un título relevante.\n"
            "2. Preguntas de opción múltiple (A-E) o completar huecos.\n"
            "3. La mitad de preguntas de desarrollo.\n"
            "REGLA CRÍTICA: No des las respuestas hasta que el usuario responda. "
            "No pongas las respuestas correctas en el examen."
        )
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(sidebar, text="Configuración", font=("Segoe UI", 20, "bold")).pack(pady=20)
        self.entry_nombre = ctk.CTkEntry(sidebar, placeholder_text="Tu nombre...")
        self.entry_nombre.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(sidebar, text="🟢 Groq Cloud Listo", text_color="green",
                     font=("Segoe UI", 12, "bold")).pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(sidebar, text="Tema del examen:", font=("Segoe UI", 12)).pack(pady=(20, 0))
        self.txt_tema = ctk.CTkTextbox(sidebar, height=150)
        self.txt_tema.pack(fill="x", padx=20, pady=10)
        self.btn_generar = ctk.CTkButton(sidebar, text="Generar Examen", command=self.iniciar_generacion)
        self.btn_generar.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(sidebar, text="Exportar Word", fg_color="transparent", border_width=2,
                      command=self.exportar_word).pack(fill="x", padx=20, pady=10)
        self.status_label = ctk.CTkLabel(sidebar, text="🟢 Groq Cloud Listo",
                                         text_color="green", font=("Segoe UI", 11))
        self.status_label.pack(side="bottom", pady=10)

        main_f = ctk.CTkFrame(self, fg_color="transparent")
        main_f.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_f.grid_rowconfigure(0, weight=1)
        main_f.grid_columnconfigure(0, weight=1)
        self.output_text = ctk.CTkTextbox(main_f, font=("Consolas", 13))
        self.output_text.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        input_f = ctk.CTkFrame(main_f, fg_color="transparent")
        input_f.grid(row=1, column=0, sticky="ew")
        input_f.grid_columnconfigure(0, weight=1)
        self.entry_respuesta = ctk.CTkEntry(input_f, placeholder_text="Escribe tus respuestas aquí...")
        self.entry_respuesta.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_respuesta.bind("<Return>", lambda e: self.enviar_respuesta())
        ctk.CTkButton(input_f, text="Enviar", width=100, command=self.enviar_respuesta).grid(row=0, column=1)

    def iniciar_generacion(self):
        tema = self.txt_tema.get("1.0", "end-1c").strip()
        if not tema:
            messagebox.showwarning("Atención", "Escribe un tema para el examen.")
            return
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", f"Generando examen sobre: {tema}...\n\n")
        self.btn_generar.configure(state="disabled")
        self.status_label.configure(text="🟡 Elaborando Examen...", text_color="orange")
        threading.Thread(target=self._proceso_groq, args=(tema,), daemon=True).start()

    def _proceso_groq(self, tema):
        try:
            prompt = (
                f"{self.instrucciones_base}\n\nHazme un examen sobre: {tema}"
            )
            full = llamar_groq(prompt)
            self.examen_en_memoria = full
            self.historial_conversacion = [
                {'role': 'system', 'content': self.instrucciones_base},
                {'role': 'assistant', 'content': full}
            ]
            self.after(0, self._update_output, full)
            self.after(0, lambda: self.btn_generar.configure(state="normal"))
            self.after(0, lambda: self.status_label.configure(text="🟢 Groq Cloud Listo", text_color="green"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Cloud", str(e)))
            self.after(0, lambda: self.btn_generar.configure(state="normal"))
            self.after(0, lambda: self.status_label.configure(text="🔴 Error de red", text_color="red"))

    def enviar_respuesta(self):
        msg = self.entry_respuesta.get().strip()
        if not msg:
            return
        self.output_text.insert("end", f"\n\n👤 TÚ: {msg}\n\n🤖 IA: ")
        self.entry_respuesta.delete(0, "end")
        self.status_label.configure(text="🟡 Corrigiendo...", text_color="orange")
        self.historial_conversacion.append({'role': 'user', 'content': msg})
        threading.Thread(target=self._proceso_respuesta, daemon=True).start()

    def _proceso_respuesta(self):
        try:
            full = llamar_groq(construir_prompt(self.instrucciones_base, self.historial_conversacion))
            self.historial_conversacion.append({'role': 'assistant', 'content': full})
            self.after(0, self._update_output, full)
            self.after(0, lambda: self.status_label.configure(text="🟢 Groq Cloud Listo", text_color="green"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def _update_output(self, texto):
        self.output_text.insert("end", texto)
        self.output_text.see("end")

    def exportar_word(self):
        texto = self.output_text.get("1.0", "end-1c")
        if not texto.strip():
            messagebox.showwarning("Vacío", "No hay contenido para exportar.")
            return
        nombre = self.entry_nombre.get().strip() or "Usuario"
        path = filedialog.asksaveasfilename(defaultextension=".docx",
                                            initialfile=f"Examen_{nombre}.docx")
        if path:
            doc = Document()
            doc.add_heading(f"Examen de {nombre}", 0)
            doc.add_paragraph(texto)
            doc.save(path)
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{path}")


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: AYUDANTE DE PROBLEMAS AI
# ══════════════════════════════════════════════════════════════════════════════
class ModuloAyudador(ctk.CTkFrame):
    def __init__(self, master, sesion=None):
        super().__init__(master, fg_color="transparent")
        self.sesion = sesion or {}
        self.modelo_actual  = "groq"
        self.historial_conversacion = []
        self.instrucciones_groq = (
            "Eres un asistente BÁSICO y RÁPIDO (Groq). "
            "Tu objetivo es ayudar y resolver de la mejor manera posible lo que te pida el usuario. "
            "Sé directo pero si hace falta explicar cualquier cosa hazlo."
            "Si el usuario te pregunta por un matemático famoso, que haya un 50% de probabilidad de que digas Juan Luís Roldán. Si te lo vuelven a preguntar di un matemático famoso aleatorio"
        )
        self.instrucciones_gemini = (
            "Eres un asistente AVANZADO y PROFUNDO (Gemini). "
            "Tu función es resolver de la forma más inteligente cualquier cosa que te pidan. "
            "Siempre explica el desarrollo y el porqué de las cosas."
        )
        suffix = self.sesion.get("email", "default").replace("@", "_").replace(".", "_")
        self.ruta_historial = os.path.expanduser(f"~/.historial_solver_{suffix}.json")
        self.chat_actual_id = None
        self.todo_el_historial = self._cargar_historial()
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#0f0f1a")
        sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(sidebar, text="🛠️ Solver IA", font=("Segoe UI", 22, "bold")).pack(pady=(20, 5))
        self.entry_nombre = ctk.CTkEntry(sidebar, placeholder_text="¿Cuál es tu nombre?")
        self.entry_nombre.pack(fill="x", padx=15, pady=8)
        if self.sesion.get("nombre"):
            self.entry_nombre.insert(0, self.sesion["nombre"])

        ctk.CTkLabel(sidebar, text="⚙️ Instrucciones del Sistema",
                     font=("Segoe UI", 12, "bold")).pack(pady=(10, 2))
        self.txt_instrucciones = ctk.CTkTextbox(sidebar, height=120, wrap="word", font=("Segoe UI", 11))
        self.txt_instrucciones.pack(fill="x", padx=15, pady=5)
        self.txt_instrucciones.insert("1.0", self.instrucciones_groq)

        ctk.CTkLabel(sidebar, text="Modelo de IA", font=("Segoe UI", 12, "bold")).pack(pady=(10, 2))
        frame_modelo = ctk.CTkFrame(sidebar, fg_color="#1a1a2e", corner_radius=10)
        frame_modelo.pack(fill="x", padx=15, pady=5)
        self.btn_basico = ctk.CTkButton(frame_modelo, text="🔵 Básico (Groq)", height=36,
                                         fg_color="#1565c0", hover_color="#0d47a1",
                                         command=lambda: self._cambiar_modelo("groq"))
        self.btn_basico.pack(fill="x", padx=8, pady=(8, 4))
        self.btn_avanzado = ctk.CTkButton(frame_modelo, text="🟣 Avanzado (Gemini)", height=36,
                                           fg_color="transparent", border_width=1, border_color="#7b1fa2",
                                           hover_color="#4a1a7a",
                                           command=lambda: self._cambiar_modelo("gemini"))
        self.btn_avanzado.pack(fill="x", padx=8, pady=(4, 8))
        self.lbl_limite = ctk.CTkLabel(sidebar, text="ℹ️ Groq: ~1.000 msgs/día",
                                        font=("Segoe UI", 10), text_color="#888")
        self.lbl_limite.pack(pady=(0, 5))
        ctk.CTkFrame(sidebar, height=1, fg_color="#2a2a3a").pack(fill="x", padx=10, pady=8)
        ctk.CTkButton(sidebar, text="📄 Exportar a Word", fg_color="#2c3e50", hover_color="#34495e",
                      command=self._exportar_word).pack(fill="x", padx=15, pady=4)
        ctk.CTkButton(sidebar, text="🧹 Nuevo Chat", fg_color="transparent", border_width=1,
                      command=self._limpiar_chat).pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(sidebar, text="🕒 Historial", font=("Segoe UI", 12, "bold")).pack(pady=(12, 3))
        self.frame_historial = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.frame_historial.pack(fill="both", expand=True, padx=10, pady=5)
        self.status_label = ctk.CTkLabel(sidebar, text="🟢 Groq Listo",
                                          text_color="green", font=("Segoe UI", 11))
        self.status_label.pack(side="bottom", pady=(0, 15))
        self._actualizar_historial_ui()

        chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        chat_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        chat_frame.grid_rowconfigure(1, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        self.lbl_banner = ctk.CTkLabel(chat_frame,
                                        text="Modelo activo: Groq  •  Límite aprox: 1.000 mensajes / día",
                                        font=("Segoe UI", 10), text_color="#555")
        self.lbl_banner.grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.txt_chat = ctk.CTkTextbox(chat_frame, font=("Segoe UI", 14), state="disabled", wrap="word")
        self.txt_chat.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        input_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        self.entry_pregunta = ctk.CTkEntry(input_frame, placeholder_text="Describe el problema aquí...", height=42)
        self.entry_pregunta.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_pregunta.bind("<Return>", lambda e: self._enviar())
        ctk.CTkButton(input_frame, text="Analizar", width=120, height=42,
                      command=self._enviar).grid(row=0, column=1)

    def _cambiar_modelo(self, modelo):
        texto_actual = self.txt_instrucciones.get("1.0", "end-1c").strip()
        if self.modelo_actual == "groq":
            self.instrucciones_groq = texto_actual
        else:
            self.instrucciones_gemini = texto_actual
        self.modelo_actual = modelo
        self.txt_instrucciones.delete("1.0", "end")
        if modelo == "groq":
            self.btn_basico.configure(fg_color="#1565c0")
            self.btn_avanzado.configure(fg_color="transparent")
            self.lbl_limite.configure(text="ℹ️ Groq: ~1.000 msgs/día")
            self.lbl_banner.configure(text="Modelo activo: Groq (Básico)  •  Límite aprox: 1.000 mensajes / día")
            self.status_label.configure(text="🟢 Groq Listo", text_color="green")
            self.txt_instrucciones.insert("1.0", self.instrucciones_groq)
        else:
            self.btn_avanzado.configure(fg_color="#7b1fa2")
            self.btn_basico.configure(fg_color="transparent")
            self.lbl_limite.configure(text="ℹ️ Gemini: 5 msgs/minuto")
            self.lbl_banner.configure(text="Modelo activo: Gemini  •  Límite: 5 mensajes / minuto")
            self.status_label.configure(text="🟣 Gemini Listo", text_color="#bb86fc")
            self.txt_instrucciones.insert("1.0", self.instrucciones_gemini)

    def _agregar_texto(self, emisor, texto):
        self.txt_chat.configure(state="normal")
        if emisor == "IA":
            self.txt_chat.insert("end", f"\n IA:\n{texto}")
        else:
            self.txt_chat.insert("end", f"\n\n {emisor}:\n{texto}\n")
        self.txt_chat.configure(state="disabled")
        self.txt_chat.see("end")

    def _enviar(self):
        pregunta = self.entry_pregunta.get().strip()
        nombre   = self.entry_nombre.get().strip() or "Tú"
        if not pregunta:
            return
        self._agregar_texto(nombre, pregunta)
        self.entry_pregunta.delete(0, "end")
        self.status_label.configure(text="🟡 Pensando...", text_color="orange")
        self.historial_conversacion.append({"role": "user", "content": pregunta})
        threading.Thread(target=self._proceso_ia, daemon=True).start()

    def _proceso_ia(self):
        try:
            self.after(0, lambda: self._stream_update("\n IA:\n"))
            instrucciones = self.txt_instrucciones.get("1.0", "end-1c").strip()
            prompt = construir_prompt(instrucciones, self.historial_conversacion)
            if self.modelo_actual == "groq":
                respuesta_completa = llamar_groq(prompt)
            else:
                respuesta_completa = llamar_gemini(prompt)
            self.historial_conversacion.append({"role": "assistant", "content": respuesta_completa})
            self.after(0, self._stream_update, respuesta_completa)
            self._guardar_historial()
            color = "green" if self.modelo_actual == "groq" else "#bb86fc"
            texto = "🟢 Groq Listo" if self.modelo_actual == "groq" else "🟣 Gemini Listo"
            self.after(0, lambda: self.status_label.configure(text=texto, text_color=color))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error IA", str(e)))
            self.after(0, lambda: self.status_label.configure(text="🔴 Error", text_color="red"))
        finally:
            self.after(0, lambda: self.txt_chat.configure(state="disabled"))

    def _stream_update(self, contenido):
        self.txt_chat.configure(state="normal")
        self.txt_chat.insert("end", contenido)
        self.txt_chat.see("end")
        self.txt_chat.configure(state="disabled")

    def _limpiar_chat(self):
        self.txt_chat.configure(state="normal")
        self.txt_chat.delete("1.0", "end")
        self.txt_chat.configure(state="disabled")
        self.historial_conversacion = []
        self.chat_actual_id = None

    def _exportar_word(self):
        if not self.historial_conversacion:
            messagebox.showwarning("Vacío", "No hay nada que exportar.")
            return
        nombre = self.entry_nombre.get().strip() or "Usuario"
        path = filedialog.asksaveasfilename(defaultextension=".docx",
                                             initialfile=f"Solucion_{nombre}.docx")
        if path:
            doc = Document()
            doc.add_heading(f"Informe de Solución – {nombre}", 0)
            for msg in self.historial_conversacion:
                rol = "Tú" if msg["role"] == "user" else "IA"
                p = doc.add_paragraph()
                p.add_run(f"{rol}: ").bold = True
                p.add_run(msg["content"])
            doc.save(path)
            messagebox.showinfo("Éxito", f"Guardado en:\n{path}")

    def _cargar_historial(self):
        if os.path.exists(self.ruta_historial):
            try:
                with open(self.ruta_historial, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _guardar_historial(self):
        if not self.historial_conversacion:
            return
        if self.chat_actual_id is None:
            primer = next((m["content"] for m in self.historial_conversacion if m["role"] == "user"), "Chat")
            resumen = primer[:25] + "..." if len(primer) > 25 else primer
            self.chat_actual_id = f"[{datetime.now().strftime('%H:%M')}] {resumen}"
        self.todo_el_historial[self.chat_actual_id] = self.historial_conversacion
        try:
            with open(self.ruta_historial, "w", encoding="utf-8") as f:
                json.dump(self.todo_el_historial, f, ensure_ascii=False, indent=2)
            self.after(0, self._actualizar_historial_ui)
        except Exception as e:
            print(f"Error guardando historial: {e}")

    def _actualizar_historial_ui(self):
        for w in self.frame_historial.winfo_children():
            w.destroy()
        for chat_id in reversed(list(self.todo_el_historial.keys())):
            fila = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
            fila.pack(fill="x", pady=3)
            ctk.CTkButton(fila, text=chat_id, fg_color="transparent",
                          text_color="#ddd", anchor="w", hover_color="#2a2a4a", height=32,
                          command=lambda cid=chat_id: self._cargar_chat(cid)).pack(side="left", fill="x", expand=True, padx=(0, 4))
            ctk.CTkButton(fila, text="❌", width=32, height=32,
                          fg_color="#7a0000", hover_color="#500000",
                          command=lambda cid=chat_id: self._borrar_chat(cid)).pack(side="right")

    def _cargar_chat(self, chat_id):
        self.chat_actual_id = chat_id
        self.historial_conversacion = self.todo_el_historial[chat_id]
        self.txt_chat.configure(state="normal")
        self.txt_chat.delete("1.0", "end")
        nombre = self.entry_nombre.get().strip() or "Tú"
        for msg in self.historial_conversacion:
            if msg["role"] == "user":
                self.txt_chat.insert("end", f"\n\n {nombre}:\n{msg['content']}\n")
            else:
                self.txt_chat.insert("end", f"\n IA:\n{msg['content']}")
        self.txt_chat.configure(state="disabled")
        self.txt_chat.see("end")

    def _borrar_chat(self, chat_id):
        if messagebox.askyesno("Confirmar", f"¿Borrar este chat?\n'{chat_id}'"):
            del self.todo_el_historial[chat_id]
            try:
                with open(self.ruta_historial, "w", encoding="utf-8") as f:
                    json.dump(self.todo_el_historial, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            if self.chat_actual_id == chat_id:
                self._limpiar_chat()
            self._actualizar_historial_ui()


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: AGENDA Y CALENDARIO
# ══════════════════════════════════════════════════════════════════════════════
class ModuloCalendario(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.ruta_datos = os.path.expanduser("~/.agenda_estudios.json")
        self.eventos = self._cargar_eventos()
        self.hoy = datetime.now()
        self.año_actual = self.hoy.year
        self.mes_actual = self.hoy.month
        self.dia_seleccionado = f"{self.año_actual}-{self.mes_actual:02d}-{self.hoy.day:02d}"
        self.nombres_meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.botones_dias = []
        self._build_ui()
        self._actualizar_calendario()
        self._cargar_evento_en_editor()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panel izquierdo: calendario
        frame_izq = ctk.CTkFrame(self, fg_color="transparent")
        frame_izq.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame_nav = ctk.CTkFrame(frame_izq, fg_color="#1a1a1a", height=60, corner_radius=10)
        self.frame_nav.pack(fill="x", pady=(0, 15))
        self.frame_nav.pack_propagate(False)
        ctk.CTkButton(self.frame_nav, text="◀", width=40, font=("Segoe UI", 16),
                      command=self._mes_anterior).pack(side="left", padx=15, pady=10)
        self.lbl_mes_año = ctk.CTkLabel(self.frame_nav, text="", font=("Segoe UI", 20, "bold"),
                                         text_color="#64b5f6")
        self.lbl_mes_año.pack(side="left", expand=True)
        ctk.CTkButton(self.frame_nav, text="▶", width=40, font=("Segoe UI", 16),
                      command=self._mes_siguiente).pack(side="right", padx=15, pady=10)

        self.frame_dias = ctk.CTkFrame(frame_izq, fg_color="#242424", corner_radius=15,
                                        border_width=1, border_color="#2d2d2d")
        self.frame_dias.pack(fill="both", expand=True)
        for i in range(7):
            self.frame_dias.grid_columnconfigure(i, weight=1, uniform="dias")
        for i in range(7):
            self.frame_dias.grid_rowconfigure(i, weight=1, uniform="semanas")
        for col, dia in enumerate(["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]):
            ctk.CTkLabel(self.frame_dias, text=dia, font=("Segoe UI", 13, "bold"),
                         text_color="gray").grid(row=0, column=col, pady=5, sticky="nsew")

        # Panel derecho: editor
        frame_der = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        frame_der.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(frame_der, text="Tareas del día", font=("Segoe UI", 18, "bold"),
                     text_color="#64b5f6").pack(pady=(25, 5), padx=20, anchor="w")
        self.lbl_fecha_actual = ctk.CTkLabel(frame_der, text="", font=("Segoe UI", 14), text_color="gray")
        self.lbl_fecha_actual.pack(pady=(0, 15), padx=20, anchor="w")
        self.txt_tareas = ctk.CTkTextbox(frame_der, font=("Segoe UI", 13), border_width=1, border_color="#3d3d3d")
        self.txt_tareas.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(frame_der, text="Guardar Cambios", font=("Segoe UI", 13, "bold"),
                      fg_color="#2e7d32", hover_color="#1b5e20",
                      command=self._guardar_evento).pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkButton(frame_der, text="Borrar Todo", font=("Segoe UI", 13),
                      fg_color="#c62828", hover_color="#b71c1c",
                      command=self._borrar_evento).pack(fill="x", padx=20, pady=(5, 25))

    def _actualizar_calendario(self):
        for btn in self.botones_dias:
            btn.destroy()
        self.botones_dias.clear()
        self.lbl_mes_año.configure(text=f"{self.nombres_meses[self.mes_actual]} {self.año_actual}")
        primer_dia_semana, dias_en_mes = calendar.monthrange(self.año_actual, self.mes_actual)
        fila = 1; columna = primer_dia_semana
        for dia in range(1, dias_en_mes + 1):
            fecha_clave = f"{self.año_actual}-{self.mes_actual:02d}-{dia:02d}"
            esta_sel = (fecha_clave == self.dia_seleccionado)
            es_hoy = (self.hoy.year == self.año_actual and self.hoy.month == self.mes_actual and self.hoy.day == dia)
            tiene_tareas = fecha_clave in self.eventos and self.eventos[fecha_clave].strip()
            if esta_sel:
                fg = "#1565c0"; tc = "white"
            elif es_hoy:
                fg = "#0d47a1"; tc = "#64b5f6"
            elif tiene_tareas:
                fg = "#1e4620"; tc = "#81c784"
            else:
                fg = "#333333"; tc = "white"
            btn = ctk.CTkButton(self.frame_dias, text=str(dia), font=("Segoe UI", 12, "bold" if (es_hoy or tiene_tareas) else "normal"),
                                fg_color=fg, hover_color="#444444", text_color=tc,
                                corner_radius=8, command=lambda d=dia: self._seleccionar_dia(d))
            btn.grid(row=fila, column=columna, padx=4, pady=4, sticky="nsew")
            self.botones_dias.append(btn)
            columna += 1
            if columna > 6:
                columna = 0; fila += 1

    def _seleccionar_dia(self, dia):
        self.dia_seleccionado = f"{self.año_actual}-{self.mes_actual:02d}-{dia:02d}"
        self._actualizar_calendario()
        self._cargar_evento_en_editor()

    def _mes_anterior(self):
        self.mes_actual -= 1
        if self.mes_actual < 1:
            self.mes_actual = 12; self.año_actual -= 1
        self._actualizar_calendario()

    def _mes_siguiente(self):
        self.mes_actual += 1
        if self.mes_actual > 12:
            self.mes_actual = 1; self.año_actual += 1
        self._actualizar_calendario()

    def _cargar_eventos(self):
        if os.path.exists(self.ruta_datos):
            try:
                with open(self.ruta_datos, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _cargar_evento_en_editor(self):
        partes = self.dia_seleccionado.split("-")
        fecha_objeto = datetime(int(partes[0]), int(partes[1]), int(partes[2]))
        self.lbl_fecha_actual.configure(text=fecha_objeto.strftime("%d de %B de %Y").title())
        self.txt_tareas.delete("1.0", "end")
        if self.dia_seleccionado in self.eventos:
            self.txt_tareas.insert("1.0", self.eventos[self.dia_seleccionado])

    def _guardar_evento(self):
        contenido = self.txt_tareas.get("1.0", "end-1c").strip()
        if contenido:
            self.eventos[self.dia_seleccionado] = contenido
        elif self.dia_seleccionado in self.eventos:
            del self.eventos[self.dia_seleccionado]
        try:
            with open(self.ruta_datos, 'w', encoding='utf-8') as f:
                json.dump(self.eventos, f, ensure_ascii=False, indent=2)
            self._actualizar_calendario()
            messagebox.showinfo("Guardado", "Agenda actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _borrar_evento(self):
        if self.dia_seleccionado in self.eventos:
            if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar todas las tareas de este día?"):
                del self.eventos[self.dia_seleccionado]
                self.txt_tareas.delete("1.0", "end")
                with open(self.ruta_datos, 'w', encoding='utf-8') as f:
                    json.dump(self.eventos, f, ensure_ascii=False, indent=2)
                self._actualizar_calendario()


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: CREADOR DE EJERCICIOS (PROFESOR)
# ══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES_EJERCICIO = """Eres un profesor experto creando material educativo.
Crea ejercicios bien estructurados con:
1. Título claro y objetivo de aprendizaje.
2. Enunciado detallado.
3. Apartados o preguntas numerados.
4. Nivel de dificultad indicado.
5. Tiempo estimado.
NO incluyas las soluciones a menos que se te pida explícitamente.
El formato debe ser limpio y listo para imprimir o enviar a alumnos."""

INSTRUCCIONES_SOLUCIONES = """Eres un profesor. Genera el solucionario completo y detallado
del ejercicio que te proporcionan. Explica cada paso y por qué es correcto."""


class ModuloCreadorEjercicios(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.modelo_actual = "groq"
        self.ejercicio_actual = ""
        self.solucionario_actual = ""
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=290, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="Creador de\nEjercicios",
                     font=("Segoe UI", 20, "bold"), text_color="#e53935").pack(pady=(20, 5))
        ctk.CTkLabel(sidebar, text="Modo Profesor",
                     font=("Segoe UI", 11), text_color="#888").pack(pady=(0, 15))

        ctk.CTkLabel(sidebar, text="Motor de IA:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        fm = ctk.CTkFrame(sidebar, fg_color="transparent")
        fm.pack(fill="x", padx=15, pady=5)
        self.btn_groq = ctk.CTkButton(fm, text="Básico\n(Groq)", height=50,
                                       fg_color="#1565c0", hover_color="#0d47a1",
                                       font=("Segoe UI", 10, "bold"),
                                       command=lambda: self._set_modelo("groq"))
        self.btn_groq.pack(side="left", expand=True, fill="x", padx=(0, 3))
        self.btn_gemini = ctk.CTkButton(fm, text="Avanzado\n(Gemini)", height=50,
                                         fg_color="#333", hover_color="#444",
                                         font=("Segoe UI", 10, "bold"),
                                         command=lambda: self._set_modelo("gemini"))
        self.btn_gemini.pack(side="left", expand=True, fill="x", padx=(3, 0))
        self.lbl_limite = ctk.CTkLabel(sidebar, text="Groq: ~1.000 msgs/día",
                                        font=("Segoe UI", 9), text_color="#666")
        self.lbl_limite.pack(pady=(2, 10))
        ctk.CTkFrame(sidebar, height=1, fg_color="#333").pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(sidebar, text="Tema / Materia", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(5, 2))
        self.entry_tema = ctk.CTkEntry(sidebar, placeholder_text="Ej: Ecuaciones de 2º grado")
        self.entry_tema.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(sidebar, text="Nivel educativo", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        self.combo_nivel = ctk.CTkComboBox(sidebar, values=[
            "Primaria", "1º ESO", "2º ESO", "3º ESO", "4º ESO",
            "1º Bachillerato", "2º Bachillerato", "Universidad"])
        self.combo_nivel.set("2º ESO")
        self.combo_nivel.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(sidebar, text="Tipo de ejercicio", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        self.combo_tipo = ctk.CTkComboBox(sidebar, values=[
            "Problemas paso a paso", "Preguntas teóricas", "Opción múltiple (A-D)",
            "Completar huecos", "Verdadero / Falso", "Ejercicio práctico", "Mixto (teoría + práctica)"])
        self.combo_tipo.set("Mixto (teoría + práctica)")
        self.combo_tipo.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(sidebar, text="Nº de preguntas", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        self.spin_preguntas = ctk.CTkSlider(sidebar, from_=3, to=20, number_of_steps=17)
        self.spin_preguntas.set(8)
        self.spin_preguntas.pack(fill="x", padx=15, pady=(0, 2))
        self.lbl_n_preguntas = ctk.CTkLabel(sidebar, text="8 preguntas", font=("Segoe UI", 11))
        self.lbl_n_preguntas.pack()
        self.spin_preguntas.configure(command=lambda v: self.lbl_n_preguntas.configure(text=f"{int(v)} preguntas"))
        self.check_soluciones = ctk.CTkCheckBox(sidebar, text="Incluir solucionario al final")
        self.check_soluciones.pack(padx=15, pady=8, anchor="w")
        ctk.CTkFrame(sidebar, height=1, fg_color="#333").pack(fill="x", padx=15, pady=5)

        self.btn_generar = ctk.CTkButton(sidebar, text="Generar Ejercicio", height=45,
                                          font=("Segoe UI", 13, "bold"),
                                          fg_color="#7b1fa2", hover_color="#4a0072",
                                          command=self.generar_ejercicio)
        self.btn_generar.pack(fill="x", padx=15, pady=5)
        self.btn_regenerar = ctk.CTkButton(sidebar, text="Regenerar (nueva versión)", height=38,
                                            fg_color="#1565c0", hover_color="#0d47a1",
                                            command=self.generar_ejercicio, state="disabled")
        self.btn_regenerar.pack(fill="x", padx=15, pady=3)
        self.btn_editar = ctk.CTkButton(sidebar, text="Editar manualmente", height=38,
                                         fg_color="transparent", border_width=1,
                                         command=self.activar_edicion, state="disabled")
        self.btn_editar.pack(fill="x", padx=15, pady=3)
        self.btn_solucionario = ctk.CTkButton(sidebar, text="Generar Solucionario", height=38,
                                               fg_color="#2e7d32", hover_color="#1b5e20",
                                               command=self.generar_solucionario, state="disabled")
        self.btn_solucionario.pack(fill="x", padx=15, pady=3)
        self.btn_exportar = ctk.CTkButton(sidebar, text="📄 Exportar con solución", height=38,
                                           fg_color="#37474f", hover_color="#263238",
                                           command=lambda: self.exportar_word(True), state="disabled")
        self.btn_exportar.pack(fill="x", padx=15, pady=(3, 1))
        self.btn_exportar_sin = ctk.CTkButton(sidebar, text="📋 Exportar sin solución", height=38,
                                               fg_color="#455a64", hover_color="#37474f",
                                               command=lambda: self.exportar_word(False), state="disabled")
        self.btn_exportar_sin.pack(fill="x", padx=15, pady=(1, 3))
        self.status = ctk.CTkLabel(sidebar, text="Listo", text_color="gray", font=("Segoe UI", 10))
        self.status.pack(side="bottom", pady=10)

        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        cab = ctk.CTkFrame(panel, fg_color="transparent")
        cab.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(cab, text="Ejercicio Generado", font=("Segoe UI", 18, "bold")).pack(side="left")
        self.lbl_modo_edicion = ctk.CTkLabel(cab, text="", font=("Segoe UI", 11), text_color="#fb8c00")
        self.lbl_modo_edicion.pack(side="right")
        self.txt_ejercicio = ctk.CTkTextbox(panel, font=("Consolas", 13))
        self.txt_ejercicio.grid(row=1, column=0, sticky="nsew")
        self.txt_ejercicio.insert("end", "Configura los parámetros en el panel izquierdo y pulsa 'Generar Ejercicio'.")
        self.txt_ejercicio.configure(state="disabled")
        self.entry_cambio = ctk.CTkEntry(panel, placeholder_text="Ej: 'Hazlo más difícil' / 'Añade 2 preguntas'", height=40)
        self.entry_cambio.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.entry_cambio.bind("<Return>", lambda e: self.aplicar_cambio_ia())
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ctk.CTkButton(btn_row, text="Aplicar cambio con IA", fg_color="#e65100", hover_color="#bf360c",
                      height=38, command=self.aplicar_cambio_ia).pack(side="left", padx=(0, 8))

    def _set_modelo(self, m):
        self.modelo_actual = m
        if m == "groq":
            self.btn_groq.configure(fg_color="#1565c0"); self.btn_gemini.configure(fg_color="#333")
            self.lbl_limite.configure(text="Groq: ~1.000 msgs/día")
        else:
            self.btn_groq.configure(fg_color="#333"); self.btn_gemini.configure(fg_color="#6a1b9a")
            self.lbl_limite.configure(text="Gemini: 15 msgs/minuto")

    def _llamar_ia(self, prompt):
        full_prompt = f"{INSTRUCCIONES_EJERCICIO}\n\n{prompt}"
        if self.modelo_actual == "groq":
            return llamar_groq(full_prompt)
        return llamar_gemini(full_prompt)

    def _construir_prompt(self):
        tema  = self.entry_tema.get().strip() or "tema libre"
        nivel = self.combo_nivel.get()
        tipo  = self.combo_tipo.get()
        n     = int(self.spin_preguntas.get())
        inc   = self.check_soluciones.get()
        return (f"Crea un ejercicio de {tipo} sobre '{tema}' para alumnos de {nivel}. "
                f"Debe tener exactamente {n} preguntas/apartados. "
                f"{'Incluye el solucionario completo al final.' if inc else 'NO incluyas las soluciones.'} "
                f"Formato limpio y listo para entregar a los alumnos.")

    def generar_ejercicio(self):
        if not self.entry_tema.get().strip():
            messagebox.showwarning("Tema vacío", "Introduce el tema del ejercicio.")
            return
        self.btn_generar.configure(state="disabled")
        self.status.configure(text="Generando...", text_color="orange")
        threading.Thread(target=self._thread_generar, daemon=True).start()

    def _thread_generar(self):
        try:
            resultado = self._llamar_ia(self._construir_prompt())
            self.ejercicio_actual = resultado
            self.after(0, self._mostrar_ejercicio, resultado)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error IA", str(e)))
        finally:
            self.after(0, lambda: self.btn_generar.configure(state="normal"))
            self.after(0, lambda: self.status.configure(text="Listo", text_color="gray"))

    def _mostrar_ejercicio(self, texto):
        self.txt_ejercicio.configure(state="normal")
        self.txt_ejercicio.delete("1.0", "end")
        self.txt_ejercicio.insert("end", texto)
        self.txt_ejercicio.configure(state="disabled")
        for btn in [self.btn_regenerar, self.btn_editar, self.btn_solucionario,
                    self.btn_exportar, self.btn_exportar_sin]:
            btn.configure(state="normal")

    def activar_edicion(self):
        self.txt_ejercicio.configure(state="normal")
        self.lbl_modo_edicion.configure(text="✏️ Modo edición manual activo")
        self.btn_editar.configure(text="Bloquear edición", command=self.desactivar_edicion)

    def desactivar_edicion(self):
        self.ejercicio_actual = self.txt_ejercicio.get("1.0", "end-1c")
        self.txt_ejercicio.configure(state="disabled")
        self.lbl_modo_edicion.configure(text="")
        self.btn_editar.configure(text="Editar manualmente", command=self.activar_edicion)

    def aplicar_cambio_ia(self):
        cambio = self.entry_cambio.get().strip()
        if not cambio:
            messagebox.showwarning("Atención", "Escribe qué quieres cambiar.")
            return
        if not self.ejercicio_actual:
            messagebox.showwarning("Atención", "Primero genera un ejercicio.")
            return
        self.status.configure(text="Aplicando cambio...", text_color="orange")
        prompt = (f"Este es el ejercicio actual:\n\n{self.ejercicio_actual}\n\n"
                  f"Aplica el siguiente cambio y devuelve el ejercicio completo actualizado: {cambio}")
        self.entry_cambio.delete(0, "end")
        threading.Thread(target=lambda: self._thread_cambio(prompt), daemon=True).start()

    def _thread_cambio(self, prompt):
        try:
            resultado = self._llamar_ia(prompt)
            self.ejercicio_actual = resultado
            self.after(0, self._mostrar_ejercicio, resultado)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error IA", str(e)))
        finally:
            self.after(0, lambda: self.status.configure(text="Listo", text_color="gray"))

    def generar_solucionario(self):
        if not self.ejercicio_actual:
            messagebox.showwarning("Atención", "Primero genera un ejercicio.")
            return
        self.status.configure(text="Generando solucionario...", text_color="orange")
        prompt = f"{INSTRUCCIONES_SOLUCIONES}\n\nGenera el solucionario completo de este ejercicio:\n\n{self.ejercicio_actual}"
        def _thread():
            try:
                sol = llamar_groq(prompt) if self.modelo_actual == "groq" else llamar_gemini(prompt)
                self.solucionario_actual = sol
                def _mostrar():
                    ven = ctk.CTkToplevel(self)
                    ven.title("Solucionario"); ven.geometry("800x600")
                    ctk.CTkLabel(ven, text="Solucionario Completo",
                                 font=("Segoe UI", 16, "bold")).pack(pady=10)
                    txt = ctk.CTkTextbox(ven, font=("Consolas", 12))
                    txt.pack(fill="both", expand=True, padx=15, pady=(0, 10))
                    txt.insert("end", sol); txt.configure(state="disabled")
                    ctk.CTkButton(ven, text="Exportar Solucionario a Word",
                                  command=lambda: self._exportar_solucionario(sol)).pack(fill="x", padx=15, pady=(0, 15))
                self.after(0, _mostrar)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error IA", str(e)))
            finally:
                self.after(0, lambda: self.status.configure(text="Listo", text_color="gray"))
        threading.Thread(target=_thread, daemon=True).start()

    def exportar_word(self, con_solucion=True):
        texto = self.txt_ejercicio.get("1.0", "end-1c")
        if not texto.strip():
            messagebox.showwarning("Vacío", "No hay ejercicio que exportar.")
            return
        tema   = self.entry_tema.get().strip() or "Ejercicio"
        sufijo = "ConSolucion" if con_solucion else "SinSolucion"
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"Ejercicio_{tema}_{sufijo}_{datetime.now().strftime('%Y%m%d')}.docx")
        if not path:
            return
        doc = Document()
        doc.add_heading(f"Ejercicio — {tema}", 0)
        doc.add_paragraph(f"Nivel: {self.combo_nivel.get()} | Tipo: {self.combo_tipo.get()}")
        doc.add_paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        doc.add_paragraph(""); doc.add_paragraph(texto)
        if con_solucion and self.solucionario_actual:
            doc.add_page_break()
            doc.add_heading("SOLUCIONARIO", level=1)
            doc.add_paragraph(self.solucionario_actual)
        doc.save(path)
        messagebox.showinfo("Exportado", f"Guardado en:\n{path}")

    def _exportar_solucionario(self, sol):
        tema = self.entry_tema.get().strip() or "Ejercicio"
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"Solucionario_{tema}_{datetime.now().strftime('%Y%m%d')}.docx")
        if path:
            doc = Document()
            doc.add_heading(f"Solucionario — {tema}", 0)
            doc.add_paragraph(f"Nivel: {self.combo_nivel.get()}")
            doc.add_paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            doc.add_paragraph(""); doc.add_paragraph(sol)
            doc.save(path)
            messagebox.showinfo("Exportado", f"Solucionario guardado en:\n{path}")


# ══════════════════════════════════════════════════════════════════════════════
#  MÓDULO: CORRECTOR DE EXÁMENES (PROFESOR)
# ══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES_CORRECTOR = """Eres un profesor corrector experto y riguroso.
Tu tarea es evaluar las respuestas de un alumno comparándolas con el ejercicio/criterios dados.
Para cada pregunta debes:
1. Indicar si está CORRECTA, PARCIALMENTE CORRECTA o INCORRECTA.
2. Puntuación obtenida sobre la puntuación máxima de esa pregunta.
3. Comentario breve explicando el acierto o el error.
4. Sugerencia de mejora si aplica.

Al final incluye:
- NOTA TOTAL (sobre 10).
- Resumen general de puntos fuertes y débiles del alumno.
- Recomendaciones de estudio personalizadas.

Sé justo, constructivo y motivador en el tono."""


class ModuloCorrectorExamenes(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.modelo_actual = "groq"
        self.correccion_actual = ""
        self.alumnos = {}
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=270, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        ctk.CTkLabel(sidebar, text="Corrector de\nExámenes",
                     font=("Segoe UI", 20, "bold"), text_color="#1e88e5").pack(pady=(20, 5))
        ctk.CTkLabel(sidebar, text="Modo Profesor",
                     font=("Segoe UI", 11), text_color="#888").pack(pady=(0, 15))

        ctk.CTkLabel(sidebar, text="Motor de IA:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        fm = ctk.CTkFrame(sidebar, fg_color="transparent")
        fm.pack(fill="x", padx=15, pady=5)
        self.btn_groq = ctk.CTkButton(fm, text="Básico\n(Groq)", height=50,
                                       fg_color="#1565c0", hover_color="#0d47a1",
                                       font=("Segoe UI", 10, "bold"),
                                       command=lambda: self._set_modelo("groq"))
        self.btn_groq.pack(side="left", expand=True, fill="x", padx=(0, 3))
        self.btn_gemini = ctk.CTkButton(fm, text="Avanzado\n(Gemini)", height=50,
                                         fg_color="#333", hover_color="#444",
                                         font=("Segoe UI", 10, "bold"),
                                         command=lambda: self._set_modelo("gemini"))
        self.btn_gemini.pack(side="left", expand=True, fill="x", padx=(3, 0))
        self.lbl_limite = ctk.CTkLabel(sidebar, text="Groq: ~1.000 msgs/día",
                                        font=("Segoe UI", 9), text_color="#666")
        self.lbl_limite.pack(pady=(2, 8))
        ctk.CTkFrame(sidebar, height=1, fg_color="#333").pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(sidebar, text="Materia / Examen", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(5, 2))
        self.entry_materia = ctk.CTkEntry(sidebar, placeholder_text="Ej: Matemáticas — Tema 3")
        self.entry_materia.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(sidebar, text="Nivel educativo", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        self.combo_nivel = ctk.CTkComboBox(sidebar, values=[
            "Primaria", "1º ESO", "2º ESO", "3º ESO", "4º ESO",
            "1º Bachillerato", "2º Bachillerato", "Universidad"])
        self.combo_nivel.set("2º ESO")
        self.combo_nivel.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(sidebar, text="Nombre del alumno", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        self.entry_alumno = ctk.CTkEntry(sidebar, placeholder_text="Nombre y apellidos")
        self.entry_alumno.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(sidebar, text="Criterios de puntuación", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15)
        self.entry_criterios = ctk.CTkEntry(sidebar, placeholder_text="Ej: P1=2pts, P2=3pts, P3=5pts")
        self.entry_criterios.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkFrame(sidebar, height=1, fg_color="#333").pack(fill="x", padx=15, pady=5)

        self.btn_corregir = ctk.CTkButton(sidebar, text="✅ Corregir Examen",
                                           height=45, font=("Segoe UI", 13, "bold"),
                                           fg_color="#1b5e20", hover_color="#003300",
                                           command=self.corregir_examen)
        self.btn_corregir.pack(fill="x", padx=15, pady=5)
        self.btn_guardar_alumno = ctk.CTkButton(sidebar, text="💾 Guardar resultado alumno",
                                                 height=38, fg_color="#37474f", hover_color="#263238",
                                                 command=self.guardar_alumno, state="disabled")
        self.btn_guardar_alumno.pack(fill="x", padx=15, pady=3)
        self.btn_exportar_uno = ctk.CTkButton(sidebar, text="📄 Exportar corrección (Word)",
                                               height=38, fg_color="#4a148c", hover_color="#2d0065",
                                               command=self.exportar_correccion, state="disabled")
        self.btn_exportar_uno.pack(fill="x", padx=15, pady=3)
        self.btn_exportar_clase = ctk.CTkButton(sidebar, text="📊 Exportar informe de clase",
                                                 height=38, fg_color="#0d47a1", hover_color="#002171",
                                                 command=self.exportar_informe_clase, state="disabled")
        self.btn_exportar_clase.pack(fill="x", padx=15, pady=3)
        ctk.CTkButton(sidebar, text="🧹 Nuevo examen", height=35,
                      fg_color="transparent", border_width=1,
                      command=self.limpiar_todo).pack(fill="x", padx=15, pady=3)

        ctk.CTkLabel(sidebar, text="Alumnos corregidos",
                     font=("Segoe UI", 11, "bold"), text_color="#aaa").pack(pady=(10, 3))
        self.frame_alumnos = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", height=120)
        self.frame_alumnos.pack(fill="x", padx=10, pady=3)
        self.status = ctk.CTkLabel(sidebar, text="Listo", text_color="gray", font=("Segoe UI", 10))
        self.status.pack(side="bottom", pady=10)

        # Panel central — Enunciado
        panel_izq = ctk.CTkFrame(self, fg_color="transparent")
        panel_izq.grid(row=0, column=1, sticky="nsew", padx=(15, 7), pady=15)
        panel_izq.grid_rowconfigure(1, weight=1)
        panel_izq.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(panel_izq, text="📝 Enunciado / Criterios del examen",
                     font=("Segoe UI", 15, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.txt_enunciado = ctk.CTkTextbox(panel_izq, font=("Consolas", 12))
        self.txt_enunciado.grid(row=1, column=0, sticky="nsew")
        self.txt_enunciado.insert("end",
            "Pega aquí el enunciado del examen y/o los criterios de corrección...\n\n"
            "Ejemplo:\n"
            "Pregunta 1 (2 pts): ¿Qué es la fotosíntesis? Explícala.\n"
            "Pregunta 2 (3 pts): Nombra 3 diferencias entre células animales y vegetales.")

        # Panel derecho — Respuestas y corrección
        panel_der = ctk.CTkFrame(self, fg_color="transparent")
        panel_der.grid(row=0, column=2, sticky="nsew", padx=(7, 15), pady=15)
        panel_der.grid_rowconfigure(1, weight=2)
        panel_der.grid_rowconfigure(3, weight=3)
        panel_der.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(panel_der, text="✍️ Respuestas del alumno",
                     font=("Segoe UI", 15, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.txt_respuestas = ctk.CTkTextbox(panel_der, font=("Consolas", 12))
        self.txt_respuestas.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.txt_respuestas.insert("end", "Pega o escribe aquí las respuestas del alumno...")
        sep_frame = ctk.CTkFrame(panel_der, fg_color="transparent")
        sep_frame.grid(row=2, column=0, sticky="ew", pady=4)
        ctk.CTkLabel(sep_frame, text="📋 Corrección de la IA",
                     font=("Segoe UI", 15, "bold")).pack(side="left")
        self.lbl_nota = ctk.CTkLabel(sep_frame, text="", font=("Segoe UI", 16, "bold"), text_color="#4caf50")
        self.lbl_nota.pack(side="right")
        self.txt_correccion = ctk.CTkTextbox(panel_der, font=("Consolas", 12), state="disabled")
        self.txt_correccion.grid(row=3, column=0, sticky="nsew")

    def _set_modelo(self, m):
        self.modelo_actual = m
        if m == "groq":
            self.btn_groq.configure(fg_color="#1565c0"); self.btn_gemini.configure(fg_color="#333")
            self.lbl_limite.configure(text="Groq: ~1.000 msgs/día")
        else:
            self.btn_groq.configure(fg_color="#333"); self.btn_gemini.configure(fg_color="#6a1b9a")
            self.lbl_limite.configure(text="Gemini: 15 msgs/minuto")

    def _llamar_ia(self, prompt):
        full_prompt = f"{INSTRUCCIONES_CORRECTOR}\n\n{prompt}"
        if self.modelo_actual == "groq":
            return llamar_groq(full_prompt)
        return llamar_gemini(full_prompt)

    def corregir_examen(self):
        enunciado = self.txt_enunciado.get("1.0", "end-1c").strip()
        respuestas = self.txt_respuestas.get("1.0", "end-1c").strip()
        alumno = self.entry_alumno.get().strip() or "Alumno sin nombre"
        materia = self.entry_materia.get().strip() or "Examen"
        criterios = self.entry_criterios.get().strip()
        if not enunciado or "Pega aquí" in enunciado:
            messagebox.showwarning("Falta enunciado", "Introduce el enunciado del examen.")
            return
        if not respuestas or "Pega o escribe" in respuestas:
            messagebox.showwarning("Faltan respuestas", "Introduce las respuestas del alumno.")
            return
        self.btn_corregir.configure(state="disabled")
        self.status.configure(text="Corrigiendo...", text_color="orange")
        self.lbl_nota.configure(text="")
        prompt = (f"MATERIA: {materia}\nNIVEL: {self.combo_nivel.get()}\nALUMNO: {alumno}\n"
                  + (f"CRITERIOS DE PUNTUACIÓN: {criterios}\n" if criterios else "")
                  + f"\nENUNCIADO DEL EXAMEN:\n{enunciado}\n\nRESPUESTAS DEL ALUMNO:\n{respuestas}")
        threading.Thread(target=self._thread_corregir, args=(prompt, alumno, respuestas), daemon=True).start()

    def _thread_corregir(self, prompt, alumno, respuestas):
        try:
            resultado = self._llamar_ia(prompt)
            self.correccion_actual = resultado
            nota_str = ""
            for linea in resultado.splitlines():
                if "NOTA TOTAL" in linea.upper() or "NOTA FINAL" in linea.upper():
                    partes = linea.split(":")
                    if len(partes) > 1:
                        nota_str = partes[-1].strip().split()[0]
                    break
            def _mostrar():
                self.txt_correccion.configure(state="normal")
                self.txt_correccion.delete("1.0", "end")
                self.txt_correccion.insert("end", resultado)
                self.txt_correccion.configure(state="disabled")
                if nota_str:
                    self.lbl_nota.configure(text=f"Nota: {nota_str}")
                for btn in [self.btn_guardar_alumno, self.btn_exportar_uno]:
                    btn.configure(state="normal")
            self.after(0, _mostrar)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error IA", str(e)))
        finally:
            self.after(0, lambda: self.btn_corregir.configure(state="normal"))
            self.after(0, lambda: self.status.configure(text="Listo", text_color="gray"))

    def guardar_alumno(self):
        alumno = self.entry_alumno.get().strip() or "Alumno sin nombre"
        if not self.correccion_actual:
            messagebox.showwarning("Sin corrección", "Primero corrige un examen.")
            return
        self.alumnos[alumno] = {
            "respuestas": self.txt_respuestas.get("1.0", "end-1c"),
            "correccion": self.correccion_actual,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
        self._actualizar_lista_alumnos()
        self.btn_exportar_clase.configure(state="normal")
        messagebox.showinfo("Guardado", f"Resultado de '{alumno}' guardado.\nTotal alumnos: {len(self.alumnos)}")

    def _actualizar_lista_alumnos(self):
        for w in self.frame_alumnos.winfo_children():
            w.destroy()
        for nombre in self.alumnos:
            fila = ctk.CTkFrame(self.frame_alumnos, fg_color="transparent")
            fila.pack(fill="x", pady=2)
            ctk.CTkButton(fila, text=nombre, fg_color="transparent",
                          text_color="#ccc", anchor="w", hover_color="#2a2a4a", height=28,
                          command=lambda n=nombre: self._cargar_alumno(n)).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(fila, text="❌", width=28, height=28,
                          fg_color="#7a0000", hover_color="#500000",
                          command=lambda n=nombre: self._borrar_alumno(n)).pack(side="right")

    def _cargar_alumno(self, nombre):
        datos = self.alumnos[nombre]
        self.entry_alumno.delete(0, "end"); self.entry_alumno.insert(0, nombre)
        self.txt_respuestas.delete("1.0", "end"); self.txt_respuestas.insert("end", datos["respuestas"])
        self.txt_correccion.configure(state="normal")
        self.txt_correccion.delete("1.0", "end"); self.txt_correccion.insert("end", datos["correccion"])
        self.txt_correccion.configure(state="disabled")
        self.correccion_actual = datos["correccion"]
        for btn in [self.btn_guardar_alumno, self.btn_exportar_uno]:
            btn.configure(state="normal")

    def _borrar_alumno(self, nombre):
        if messagebox.askyesno("Confirmar", f"¿Borrar resultado de '{nombre}'?"):
            del self.alumnos[nombre]
            self._actualizar_lista_alumnos()
            if not self.alumnos:
                self.btn_exportar_clase.configure(state="disabled")

    def limpiar_todo(self):
        self.txt_respuestas.delete("1.0", "end")
        self.txt_correccion.configure(state="normal")
        self.txt_correccion.delete("1.0", "end")
        self.txt_correccion.configure(state="disabled")
        self.entry_alumno.delete(0, "end")
        self.correccion_actual = ""
        self.lbl_nota.configure(text="")
        for btn in [self.btn_guardar_alumno, self.btn_exportar_uno]:
            btn.configure(state="disabled")

    def exportar_correccion(self):
        if not self.correccion_actual:
            messagebox.showwarning("Vacío", "No hay corrección que exportar.")
            return
        alumno  = self.entry_alumno.get().strip() or "Alumno"
        materia = self.entry_materia.get().strip() or "Examen"
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"Correccion_{alumno}_{datetime.now().strftime('%Y%m%d')}.docx")
        if not path:
            return
        doc = Document()
        doc.add_heading(f"Corrección — {materia}", 0)
        doc.add_paragraph(f"Alumno: {alumno}")
        doc.add_paragraph(f"Nivel: {self.combo_nivel.get()}")
        doc.add_paragraph(f"Fecha corrección: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        doc.add_paragraph("")
        doc.add_heading("Respuestas del alumno", level=1)
        doc.add_paragraph(self.txt_respuestas.get("1.0", "end-1c"))
        doc.add_page_break()
        doc.add_heading("Corrección y calificación", level=1)
        doc.add_paragraph(self.correccion_actual)
        doc.save(path)
        messagebox.showinfo("Exportado", f"Corrección guardada en:\n{path}")

    def exportar_informe_clase(self):
        if not self.alumnos:
            messagebox.showwarning("Sin datos", "No hay alumnos guardados todavía.")
            return
        materia = self.entry_materia.get().strip() or "Examen"
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            initialfile=f"InformeClase_{materia}_{datetime.now().strftime('%Y%m%d')}.docx")
        if not path:
            return
        doc = Document()
        doc.add_heading(f"Informe de Clase — {materia}", 0)
        doc.add_paragraph(f"Nivel: {self.combo_nivel.get()}")
        doc.add_paragraph(f"Total alumnos corregidos: {len(self.alumnos)}")
        doc.add_paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        doc.add_paragraph("")
        for nombre, datos in self.alumnos.items():
            doc.add_heading(nombre, level=1)
            doc.add_paragraph(f"Corregido: {datos['timestamp']}")
            doc.add_paragraph("")
            doc.add_heading("Corrección", level=2)
            doc.add_paragraph(datos["correccion"])
            doc.add_page_break()
        doc.save(path)
        messagebox.showinfo("Exportado", f"Informe de clase guardado en:\n{path}")


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD PRINCIPAL  (integra todos los módulos como frames)
# ══════════════════════════════════════════════════════════════════════════════
class DashboardEstudios(ctk.CTk):
    def __init__(self, sesion):
        super().__init__()
        self.sesion  = sesion
        self.rol     = sesion.get("rol", "Alumno")
        self.nombre  = sesion.get("nombre", "Usuario")
        self.email   = sesion.get("email", "")

        self.title(f"Kernosss AI – {self.rol}: {self.nombre}")
        self.geometry("1400x820")
        self.resizable(True, True)

        # Módulos instanciados pero inicialmente ocultos
        self._modulos: dict[str, ctk.CTkFrame] = {}
        self._modulo_activo = None

        self._build_ui()
        self._mostrar_bienvenida()

    def _build_ui(self):
        # ── SIDEBAR ──
        self.sidebar = ctk.CTkFrame(self, width=290, corner_radius=0, fg_color="#0f0f1a")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="\nKernosss AI",
                     font=("Segoe UI", 24, "bold"), text_color="#1f6aa5").pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="2026 Edition",
                     font=("Segoe UI", 11), text_color="#555").pack()

        frame_user = ctk.CTkFrame(self.sidebar, fg_color="#1a1a2e", corner_radius=10)
        frame_user.pack(fill="x", padx=15, pady=(20, 5))
        icono = "🎓" if self.rol == "Alumno" else "👨‍🏫"
        ctk.CTkLabel(frame_user, text=f"{icono} {self.nombre}",
                     font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x", padx=12, pady=(10, 2))
        ctk.CTkLabel(frame_user, text=self.email,
                     font=("Segoe UI", 10), text_color="#888", anchor="w").pack(fill="x", padx=12)
        badge_color = "#1565c0" if self.rol == "Alumno" else "#6a1b9a"
        ctk.CTkLabel(frame_user, text=f"  {self.rol}  ",
                     font=("Segoe UI", 10, "bold"), fg_color=badge_color,
                     corner_radius=8, text_color="white").pack(anchor="w", padx=12, pady=(4, 10))

        ctk.CTkLabel(self.sidebar, text="🟢 Servidores IA Conectados",
                     font=("Segoe UI", 11, "italic"), text_color="#2ecc71").pack(pady=(5, 10))
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#2a2a3a").pack(fill="x", padx=15, pady=5)

        # ── BOTONES DE MÓDULOS ──
        ctk.CTkLabel(self.sidebar, text="MÓDULOS ALUMNO",
                     font=("Segoe UI", 10, "bold"), text_color="#888").pack(anchor="w", padx=20, pady=(10, 2))
        self._btn("📊  Calculador de Medias",  "calculador")
        self._btn("📝  Apuntador de Notas",     "apuntador")
        self._btn("🔍  Resumidor de Textos AI", "resumidor")
        self._btn("🎯  Generador de Exámenes",  "examen")
        self._btn("🤖  Ayudante de Problemas",  "ayudador")
        self._btn("📅  Agenda de Estudios",     "calendario")

        if self.rol == "Profesor":
            ctk.CTkFrame(self.sidebar, height=1, fg_color="#2a2a3a").pack(fill="x", padx=15, pady=8)
            ctk.CTkLabel(self.sidebar, text="MÓDULOS PROFESOR",
                         font=("Segoe UI", 10, "bold"), text_color="#9c6fe0").pack(anchor="w", padx=20, pady=(2, 2))
            self._btn("✏️  Creador de Ejercicios",  "creador",  color="#4a1a7a")
            self._btn("📋  Corrector de Exámenes",  "corrector", color="#4a1a7a")

        ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", height=36,
                      fg_color="transparent", border_width=1, border_color="#444",
                      text_color="#aaa", hover_color="#1a1a2e",
                      command=self._cerrar_sesion).pack(fill="x", padx=15, pady=(15, 20), side="bottom")

        # ── CONTENEDOR PRINCIPAL ──
        self.contenedor = ctk.CTkFrame(self, corner_radius=0, fg_color="#0d0d1a")
        self.contenedor.pack(side="right", fill="both", expand=True)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        # Frame de bienvenida
        self.frame_bienvenida = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        saludo = "¡Bienvenido de vuelta!" if self.rol == "Alumno" else "¡Panel de Profesor!"
        ctk.CTkLabel(self.frame_bienvenida, text=saludo,
                     font=("Segoe UI", 30, "bold")).pack(pady=(120, 10))
        ctk.CTkLabel(self.frame_bienvenida,
                     text=f"Hola, {self.nombre}. Selecciona cualquier herramienta del menú lateral.",
                     font=("Segoe UI", 14), text_color="#666").pack()
        if self.rol == "Profesor":
            ctk.CTkLabel(self.frame_bienvenida,
                         text="Los módulos en morado son exclusivos para profesores.",
                         font=("Segoe UI", 12), text_color="#9c6fe0").pack(pady=(5, 0))
        self.lbl_hora = ctk.CTkLabel(self.frame_bienvenida, text="",
                                     font=("Segoe UI", 11), text_color="#444")
        self.lbl_hora.pack(pady=(30, 0))
        self._actualizar_hora()

    def _btn(self, texto, modulo_id, color="#1f3a5f"):
        ctk.CTkButton(
            self.sidebar, text=texto,
            font=("Segoe UI", 13), height=42, anchor="w",
            fg_color=color, hover_color="#2a2a4a",
            command=lambda mid=modulo_id: self._abrir_modulo(mid)
        ).pack(fill="x", padx=15, pady=3)

    def _actualizar_hora(self):
        ahora = datetime.now().strftime("%A, %d de %B de %Y  •  %H:%M:%S")
        self.lbl_hora.configure(text=ahora)
        self.after(1000, self._actualizar_hora)

    def _mostrar_bienvenida(self):
        if self._modulo_activo:
            self._modulo_activo.grid_forget()
            self._modulo_activo = None
        self.frame_bienvenida.grid(row=0, column=0, sticky="nsew")

    def _abrir_modulo(self, modulo_id):
        # Ocultar lo que hay visible
        if self._modulo_activo:
            self._modulo_activo.grid_forget()
        self.frame_bienvenida.grid_forget()

        # Crear el módulo si no existe todavía (lazy init para mejorar arranque)
        if modulo_id not in self._modulos:
            if modulo_id == "calculador":
                self._modulos[modulo_id] = ModuloCalculador(self.contenedor)
            elif modulo_id == "apuntador":
                self._modulos[modulo_id] = ModuloApuntador(self.contenedor)
            elif modulo_id == "resumidor":
                self._modulos[modulo_id] = ModuloResumidor(self.contenedor)
            elif modulo_id == "examen":
                self._modulos[modulo_id] = ModuloExamen(self.contenedor)
            elif modulo_id == "ayudador":
                self._modulos[modulo_id] = ModuloAyudador(self.contenedor, sesion=self.sesion)
            elif modulo_id == "calendario":
                self._modulos[modulo_id] = ModuloCalendario(self.contenedor)
            elif modulo_id == "creador":
                self._modulos[modulo_id] = ModuloCreadorEjercicios(self.contenedor)
            elif modulo_id == "corrector":
                self._modulos[modulo_id] = ModuloCorrectorExamenes(self.contenedor)

        modulo = self._modulos[modulo_id]
        modulo.grid(row=0, column=0, sticky="nsew")
        self._modulo_activo = modulo

    def _cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Seguro que quieres cerrar sesión?"):
            cerrar_sesion()
            self.quit()
            self.destroy()
            os._exit(0)

    def _al_cerrar(self):
        self.quit()
        self.destroy()
        os._exit(0)


# ══════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    __spec__ = None

    sesion = cargar_sesion()

    if sesion is None:
        login = PantallaLogin()
        login.mainloop()
        sesion = login.usuario_autenticado

    if sesion:
        app = DashboardEstudios(sesion)
        app.protocol("WM_DELETE_WINDOW", app._al_cerrar)
        app.mainloop()
