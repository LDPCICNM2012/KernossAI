import customtkinter as ctk
import threading, ollama

ctk.set_appearance_mode("system")
app = ctk.CTk()
app.title("Generador de examen")
app.geometry("700x500")

entrada = ctk.CTkEntry(app, placeholder_text="Tema del examen", width=500)
entrada.pack(padx=20, pady=15)

salida = ctk.CTkTextbox(app, width=650, height=350)
salida.pack(padx=20)

def generar():
    tema = entrada.get()
    salida.delete("1.0", "end")
    def tarea():
        stream = ollama.chat(
            model="llama3.2",
            messages=[{"role":"user", "content": tema}],
            stream=True
        )
        for chunk in stream:
            txt = chunk["message"]["content"]
            salida.after(0, lambda t=txt: salida.insert("end", t))
    threading.Thread(target=tarea).start()

ctk.CTkButton(app, text="Generar", command=generar).pack(pady=10)
app.mainloop()