import os
import json

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".kernossai")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def inicializar_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"groq_key": "", "gemini_key": ""}, f)

def guardar_keys(groq_key, gemini_key):
    inicializar_config()
    with open(CONFIG_FILE, "w") as f:
        json.dump({"groq_key": groq_key, "gemini_key": gemini_key}, f)

def obtener_keys():
    inicializar_config()
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("groq_key", ""), data.get("gemini_key", "")
    except Exception:
        return "", ""
