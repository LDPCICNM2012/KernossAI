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


def obtener_fecha_instalacion() -> Tuple[object, int, int]:
    """
    Obtiene la fecha de instalación inicial.
    Devuelve (fecha_dt, dias_transcurridos, dias_restantes_gracia).
    El período de gracia es de 15 días.
    """
    from datetime import datetime
    inicializar_config()
    data = {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        pass

    fecha_str = data.get("fecha_instalacion")
    if not fecha_str:
        fecha_str = datetime.now().isoformat()
        data["fecha_instalacion"] = fecha_str
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    try:
        dt = datetime.fromisoformat(fecha_str)
    except Exception:
        dt = datetime.now()

    dias_transcurridos = max(0, (datetime.now() - dt).days)
    dias_restantes_gracia = max(0, 15 - dias_transcurridos)
    return dt, dias_transcurridos, dias_restantes_gracia


def obtener_pase_temporal(email: str = "") -> Tuple[bool, int, str, int]:
    """
    Comprueba si el usuario tiene activo el pase temporal de 7 días y cuándo puede volver a activarlo.
    Devuelve:
      - activo (bool): Si el pase de 7 días está vigente ahora mismo.
      - dias_restantes_pase (int): Días que le quedan al pase de 7 días activo.
      - fecha_disponible_str (str): Fecha en la que podrá volver a activarlo (1 vez al mes / cada 30 días).
      - dias_para_disponible (int): Días que faltan para poder activarlo de nuevo (0 si ya está disponible).
    """
    from datetime import datetime, timedelta
    inicializar_config()
    em_key = (email or "global").strip().lower()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    pases = data.get("pases_temporales", {})
    usr_pase = pases.get(em_key) or pases.get("global", {})

    ultimo_uso_str = usr_pase.get("ultimo_uso")
    expira_str = usr_pase.get("expira")

    activo = False
    dias_restantes_pase = 0
    now = datetime.now()

    if expira_str:
        try:
            dt_exp = datetime.fromisoformat(expira_str)
            if dt_exp > now:
                activo = True
                dias_restantes_pase = max(1, (dt_exp - now).days + 1)
        except Exception:
            pass

    dias_para_disponible = 0
    fecha_disponible_str = "Disponible ahora"

    if ultimo_uso_str:
        try:
            dt_ultimo = datetime.fromisoformat(ultimo_uso_str)
            dt_proxima = dt_ultimo + timedelta(days=30)
            if dt_proxima > now:
                dias_para_disponible = max(1, (dt_proxima - now).days)
                fecha_disponible_str = dt_proxima.strftime("%d/%m/%Y")
        except Exception:
            pass

    return activo, dias_restantes_pase, fecha_disponible_str, dias_para_disponible


def guardar_activacion_pase_temporal(email: str = "") -> Tuple[bool, str]:
    """
    Activa el pase temporal de 7 días si han pasado al menos 30 días desde la última activación.
    """
    from datetime import datetime, timedelta
    inicializar_config()
    em_key = (email or "global").strip().lower()
    activo, _, fecha_disp, dias_falta = obtener_pase_temporal(em_key)
    
    if dias_falta > 0 and not activo:
        return False, f"Solo se puede activar el pase temporal 1 vez al mes. Estará disponible el {fecha_disp} (en {dias_falta} días)."

    now = datetime.now()
    expira = now + timedelta(days=7)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    if "pases_temporales" not in data:
        data["pases_temporales"] = {}

    pase_entry = {
        "ultimo_uso": now.isoformat(),
        "expira": expira.isoformat()
    }
    data["pases_temporales"][em_key] = pase_entry
    data["pases_temporales"]["global"] = pase_entry

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        return False, f"Error al guardar configuración local: {e}"

    return True, f"Hogar Temporal activado con éxito por 7 días (válido hasta el {expira.strftime('%d/%m/%Y')})."
