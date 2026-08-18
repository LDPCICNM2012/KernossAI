import os
import json
from typing import Tuple

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".kernossai")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def inicializar_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "idioma": "es",
                "groq_key": "",
                "gemini_key": "",
                "tts_voz": "es-ES-AlvaroNeural",
                "tts_velocidad": "+0%"
            }, f, indent=2)

def guardar_keys(groq_key: str, gemini_key: str):
    inicializar_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    data["groq_key"] = groq_key
    data["gemini_key"] = gemini_key
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def obtener_keys() -> Tuple[str, str]:
    inicializar_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("groq_key", ""), data.get("gemini_key", "")
    except Exception:
        return "", ""

def guardar_ajustes_tts(voz: str, velocidad: str = "+0%"):
    inicializar_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    data["tts_voz"] = voz
    data["tts_velocidad"] = velocidad
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def obtener_ajustes_tts() -> Tuple[str, str]:
    inicializar_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return (
                data.get("tts_voz", "es-ES-AlvaroNeural"),
                data.get("tts_velocidad", "+0%")
            )
    except Exception:
        return "es-ES-AlvaroNeural", "+0%"

def guardar_idioma(idioma: str):
    inicializar_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    data["idioma"] = idioma
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def obtener_idioma() -> str:
    inicializar_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("idioma", "es")
    except Exception:
        return "es"
