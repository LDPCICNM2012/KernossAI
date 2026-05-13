import customtkinter as ctk
from tkinter import messagebox

# Configurar el tema oscuro/claro según el sistema
ctk.set_appearance_mode("dark")
# Usar un tema de color moderno y profesional (azul)
ctk.set_default_color_theme("blue")

class AppCalculadora(ctk.CTk):
    def __init__(self):
        # Heredar de CTk para crear una ventana moderna
        super().__init__()

        # Establecer el título de la ventana
        self.title("Calculadora de Medias")
        # Definir dimensiones de la ventana (ancho x alto)
        self.geometry("950x900")
        # Agregar un poco de padding para que no se vea pegado a los bordes
        self.resizable(False, False)
        
        # Configurar el grid principal para centrar contenido horizontalmente
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # ───── SECCIÓN DE TÍTULO ─────
        # Frame superior para el título con un color de fondo sutil
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.pack(fill="x", padx=20, pady=(20, 15))
        
        # Label con el título principal
        label_titulo = ctk.CTkLabel(
            frame_titulo, 
            # Texto del encabezado
            text="Calculadora de Medias", 
            # Fuente: Segoe UI, tamaño 32, negrita
            font=("Segoe UI", 32, "bold"),
            # Color dinámico según tema claro/oscuro
            text_color=["#0d47a1", "#64b5f6"]
        )
        label_titulo.pack()

        # Subtítulo descriptivo con fuente más pequeña
        label_subtitulo = ctk.CTkLabel(
            frame_titulo,
            # Texto informativo
            text="Organiza y calcula el promedio de tus calificaciones",
            # Fuente más pequeña y ligera
            font=("Segoe UI", 12),
            # Color gris para menos énfasis
            text_color=["#424242", "#bdbdbd"]
        )
        label_subtitulo.pack(pady=(3, 0))

        # ───── SECCIÓN DE ENTRADA PRINCIPAL ─────
        # Frame contenedor principal con esquinas redondeadas
        self.frame_entrada = ctk.CTkFrame(
            self, 
            # Radio de las esquinas redondeadas (20px)
            corner_radius=12,
            # Borde visible de 1px
            border_width=1,
            # Color de borde oscuro/claro según tema
            border_color=["#e0e0e0", "#333333"]
        )
        self.frame_entrada.pack(padx=25, pady=15, fill="both", expand=False)
        
        # Configurar dos columnas iguales dentro del frame
        self.frame_entrada.grid_columnconfigure((0, 1), weight=1)

        # Label para el campo de nombre de materia
        label_materia = ctk.CTkLabel(
            self.frame_entrada, 
            # Texto descriptivo
            text="Materia o Asignatura", 
            # Fuente más pequeña que el título
            font=("Segoe UI", 13, "bold"),
            # Color oscuro
            text_color=["#212121", "#f5f5f5"]
        )
        label_materia.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        # Campo de entrada para el nombre de la materia
        self.entrada_nombre = ctk.CTkEntry(
            self.frame_entrada, 
            # Texto de ayuda que desaparece al escribir
            placeholder_text="Ej: Matemáticas, Física...",
            # Alto del campo de entrada
            height=40,
            # Fuente proporcional
            font=("Segoe UI", 12),
            # Borde sutil
            border_width=1
        )
        self.entrada_nombre.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        # Label para nota directa (sin subnotas)
        label_nota = ctk.CTkLabel(
            self.frame_entrada, 
            # Texto descriptivo
            text="Nota Directa", 
            # Fuente igual al anterior
            font=("Segoe UI", 13, "bold"),
            # Color oscuro
            text_color=["#212121", "#f5f5f5"]
        )
        label_nota.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")

        # Campo de entrada para la nota numérica
        self.entrada_nota_directa = ctk.CTkEntry(
            self.frame_entrada, 
            # Texto de ayuda
            placeholder_text="Ej: 9.5",
            # Alto similar a la entrada anterior
            height=40,
            # Fuente proporcional
            font=("Segoe UI", 12),
            # Borde sutil
            border_width=1
        )
        self.entrada_nota_directa.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        # ───── SECCIÓN DE BOTONES DE ACCIÓN ─────
        # Frame para agrupar los botones de manera ordenada
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.pack(fill="x", padx=25, pady=12)
        
        # Distribuir dos columnas iguales para los botones
        frame_botones.grid_columnconfigure((0, 1), weight=1)

        # Botón para guardar una nota simple
        self.btn_agregar = ctk.CTkButton(
            frame_botones, 
            # Texto del botón con icono
            text="Guardar Nota",
            # Función que se ejecuta al presionar
            command=self.agregar_nota_principal,
            # Color verde para acción positiva
            fg_color="#4caf50",
            # Color más oscuro al pasar el mouse
            hover_color="#388e3c",
            # Alto del botón
            height=40,
            # Fuente legible
            font=("Segoe UI", 12, "bold"),
            # Color del texto blanco
            text_color="white"
        )
        self.btn_agregar.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        # Botón para agregar subnotas (notas derivadas)
        self.btn_subnotas = ctk.CTkButton(
            frame_botones, 
            # Texto descriptivo
            text="Agregar Subnotas",
            # Función cuando se presiona
            command=self.gestionar_subnotas,
            # Fondo transparente con borde
            fg_color="transparent",
            # Borde visible de 2px
            border_width=2,
            # Color del borde (cian/azul)
            border_color=["#0288d1", "#4dd0e1"],
            # Alto consistente
            height=40,
            # Fuente similar
            font=("Segoe UI", 12, "bold")
        )
        self.btn_subnotas.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # ───── SECCIÓN DE HISTORIAL/REGISTRO ─────
        # Label para la sección de notas guardadas
        label_historial = ctk.CTkLabel(
            self, 
            # Título de la sección
            text="Registro de Notas",
            # Fuente grande pero no excesiva
            font=("Segoe UI", 16, "bold"),
            # Color oscuro
            text_color=["#212121", "#f5f5f5"]
        )
        label_historial.pack(pady=(20, 8), padx=25, anchor="w")

        # Caja de texto para mostrar todas las notas guardadas
        self.salida_texto = ctk.CTkTextbox(
            self, 
            # Ancho del área de texto
            width=900,
            # Altura del área de texto
            height=350,
            # Fuente monoespaciada para alineación
            font=("Courier New", 11),
            # Esquinas redondeadas suaves
            corner_radius=10,
            # Borde visible
            border_width=1,
            # No editable por el usuario
            state="disabled"
        )
        self.salida_texto.pack(padx=25, pady=(0, 20), fill="both", expand=True)

        # ───── SECCIÓN DE RESULTADO FINAL ─────
        # Botón para calcular y mostrar el promedio final
        self.btn_calcular = ctk.CTkButton(
            self, 
            # Texto del botón principal
            text="Calcular Promedio Final",
            # Función para calcular resultado
            command=self.calcular_total_final,
            # Alto visual más prominente
            height=55,
            # Ancho controlado
            width=450,
            # Fuente grande y bold
            font=("Segoe UI", 14, "bold"),
            # Color azul principal
            fg_color="#0277bd",
            # Azul más oscuro al hover
            hover_color="#01579b",
            # Esquinas redondeadas
            corner_radius=10,
            # Texto blanco
            text_color="white"
        )
        self.btn_calcular.pack(pady=(0, 20))

        # Listas para almacenar los datos de notas
        # Lista que guarda los valores numéricos de todas las notas
        self.notas_finales = []
        # Lista que guarda los nombres correspondientes a cada nota
        self.nombres_notas = []

    def calcular_media(self, lista):
        # Retornar 0 si la lista está vacía (evitar división por cero)
        if not lista: 
            return 0
        # Sumar todos los elementos y dividir entre la cantidad
        return sum(lista) / len(lista)

    def gestionar_subnotas(self):
        # Obtener el nombre de la materia del campo de entrada
        nombre_principal = self.entrada_nombre.get().strip()
        # Validar que el nombre no esté vacío
        if not nombre_principal:
            # Mostrar advertencia si no hay nombre
            messagebox.showwarning("Atención", "Escribe el nombre de la asignatura primero.")
            # Salir de la función sin hacer nada
            return

        # Crear un diálogo para preguntar cuántas subnotas hay
        dialogo_cant = ctk.CTkInputDialog(text="¿Cuántas calificaciones parciales tiene?", title="Número de Subnotas")
        # Obtener la respuesta del usuario
        res_cant = dialogo_cant.get_input()
        
        # Verificar que la respuesta sea un número válido
        if res_cant and res_cant.isdigit():
            # Convertir a número entero
            cantidad = int(res_cant)
            # Lista temporal para guardar las subnotas
            subnotas_valores = []
            
            # Habilitar edición del textbox
            self.salida_texto.configure(state="normal")
            # Agregar un encabezado con el nombre de la asignatura
            self.salida_texto.insert("end", f"\n{'─'*60}\n")
            self.salida_texto.insert("end", f"  📚 {nombre_principal.upper()}\n")
            self.salida_texto.insert("end", f"{'─'*60}\n")

            # Iterar para cada subnota que debe ingresarse
            for j in range(cantidad):
                # Crear diálogo para pedir el nombre de la i-ésima subnota
                d_nom = ctk.CTkInputDialog(text=f"Nombre de la calificación {j+1}:", title="Subnota")
                # Obtener el nombre ingresado
                n_sub = d_nom.get_input()
                # Si el usuario cancela, salir del bucle
                if n_sub is None: 
                    break 

                # Crear diálogo para pedir el valor numérico de la subnota
                d_val = ctk.CTkInputDialog(text=f"Calificación de '{n_sub}':", title="Nota")
                # Obtener el valor ingresado
                v_sub = d_val.get_input()
                # Si el usuario cancela, salir del bucle
                if v_sub is None: 
                    break

                # Intentar convertir el valor a número decimal
                try:
                    # Convertir string a float
                    nota_f = float(v_sub)
                    # Agregar a la lista temporal
                    subnotas_valores.append(nota_f)
                    # Mostrar la subnota ingresada en el textbox
                    self.salida_texto.insert("end", f"    • {n_sub:25} → {nota_f:.2f}\n")
                # Si hay error de conversión
                except ValueError:
                    # Mostrar error de formato
                    messagebox.showerror("Error", "Por favor introduce un número válido.")
            
            # Si se ingresaron subnotas válidas
            if subnotas_valores:
                # Calcular el promedio de las subnotas
                nota_final = self.calcular_media(subnotas_valores)
                # Calcular el porcentaje que representa sobre el total actual
                total_notas_actuales = len(self.notas_finales) + 1
                # El porcentaje es 1/total_notas_actuales convertido a porcentaje
                porcentaje_sobre_total = (1 / total_notas_actuales) * 100
                # Guardar el nombre de la materia
                self.nombres_notas.append(nombre_principal)
                # Guardar la nota promedio calculada
                self.notas_finales.append(nota_final)
                
                # Mostrar el resultado del promedio con énfasis
                self.salida_texto.insert("end", f"  ✓ Promedio: {nota_final:.2f}\n")
                # Mostrar el porcentaje que representa sobre el total
                self.salida_texto.insert("end", f"  ⚖️  Peso sobre total: {porcentaje_sobre_total:.1f}%\n")
                self.salida_texto.insert("end", f"{'─'*60}\n\n")
                # Deshabilitar edición nuevamente
                self.salida_texto.configure(state="disabled")
                # Limpiar el campo de nombre para la siguiente materia
                self.entrada_nombre.delete(0, "end")

    def agregar_nota_principal(self):
        # Obtener el nombre de la materia del campo de entrada
        nombre = self.entrada_nombre.get().strip()
        # Obtener la nota numérica del campo de entrada
        nota_str = self.entrada_nota_directa.get().strip()

        # Validar que ambos campos tengan contenido
        if nombre and nota_str:
            # Intentar convertir a número decimal
            try:
                # Convertir string a float
                nota = float(nota_str)
                # Calcular el porcentaje que representa sobre el total
                total_notas_actuales = len(self.notas_finales) + 1
                # El porcentaje es 1/total_notas_actuales convertido a porcentaje
                porcentaje_sobre_total = (1 / total_notas_actuales) * 100
                # Guardar el nombre en la lista
                self.nombres_notas.append(nombre)
                # Guardar la nota en la lista
                self.notas_finales.append(nota)
                
                # Habilitar edición del textbox
                self.salida_texto.configure(state="normal")
                # Mostrar la nota guardada en el historial
                self.salida_texto.insert("end", f"  ✓ {nombre:25} → {nota:.2f}")
                # Mostrar el porcentaje que representa sobre el total
                self.salida_texto.insert("end", f" ({porcentaje_sobre_total:.1f}%)\n")
                # Deshabilitar edición nuevamente
                self.salida_texto.configure(state="disabled")
                
                # Limpiar campos de entrada
                self.entrada_nombre.delete(0, "end")
                self.entrada_nota_directa.delete(0, "end")
            # Si la conversión falla
            except ValueError:
                # Mostrar error de formato
                messagebox.showerror("Error", "La calificación debe ser un número (ej: 9.5).")
        # Si falta algún campo
        else:
            # Advertir al usuario que complete ambos campos
            messagebox.showwarning("Campos incompletos", "Por favor completa materia y calificación.")

    def calcular_total_final(self):
        # Validar que haya al menos una nota guardada
        if not self.notas_finales:
            # Informar que no hay datos
            messagebox.showinfo("Sin datos", "No hay calificaciones guardadas para calcular.")
            # Salir sin hacer nada
            return

        # Calcular el promedio de todas las notas
        media_total = self.calcular_media(self.notas_finales)
        
        # Habilitar edición del textbox para agregar resultado
        self.salida_texto.configure(state="normal")
        # Línea decorativa superior
        self.salida_texto.insert("end", f"\n{'═'*60}\n")
        # Línea de título del resultado
        self.salida_texto.insert("end", f"  📊 RESULTADO FINAL\n")
        # Mostrar cantidad de asignaturas
        self.salida_texto.insert("end", f"  Asignaturas: {len(self.nombres_notas)}\n")
        # Mostrar promedio general con dos decimales
        self.salida_texto.insert("end", f"  Promedio General: {media_total:.2f}\n")
        # Línea decorativa inferior
        self.salida_texto.insert("end", f"{'═'*60}\n\n")
        # Deshabilitar edición nuevamente
        self.salida_texto.configure(state="disabled")
        # Desplazar vista al final del contenido
        self.salida_texto.see("end")

# Punto de entrada del programa
if __name__ == "__main__":
    # Crear instancia de la aplicación
    app = AppCalculadora()
    # Iniciar el loop de eventos principal
    app.mainloop()
