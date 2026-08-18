import json
import os
import requests
from typing import Tuple, Dict, Any, Optional

BACKEND_URL = "https://kernosai-backend.onrender.com"
RUTA_TOKEN  = os.path.expanduser("~/.kernos_token.json")

# ── Guardar / leer token en disco ──────────────────

def _guardar_token(token: str, sesion: dict):
    try:
        with open(RUTA_TOKEN, "w", encoding="utf-8") as f:
            json.dump({"token": token, "sesion": sesion}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _leer_token() -> Tuple[str, dict]:
    """Devuelve (token, sesion) o ("", {}) si no existe."""
    if os.path.exists(RUTA_TOKEN):
        try:
            with open(RUTA_TOKEN, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("token", ""), data.get("sesion", {})
        except Exception:
            pass
    return "", {}

def borrar_token():
    if os.path.exists(RUTA_TOKEN):
        try:
            os.remove(RUTA_TOKEN)
        except Exception:
            pass

def token_guardado() -> Tuple[str, dict]:
    """
    Comprueba si hay un token válido guardado.
    Devuelve (token, sesion) si es válido, ("", {}) si no.
    """
    token, sesion = _leer_token()
    if not token:
        return "", {}
    try:
        r = requests.get(
            f"{BACKEND_URL}/auth/verificar",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            sesion.update({
                "email": data.get("email", sesion.get("email")),
                "nombre": data.get("nombre", sesion.get("nombre")),
                "rol": data.get("rol", sesion.get("rol")),
                "is_premium": data.get("is_premium", False),
                "hogar_nombre": data.get("hogar_nombre", "Hogar Principal")
            })
            _guardar_token(token, sesion)
            return token, sesion
    except Exception:
        # Si no hay internet momentáneo pero el token existe localmente
        if sesion and sesion.get("email"):
            return token, sesion
    return "", {}


# ── Login / Registro con Detección de Hogar ────────────────

def login(email: str, password: str, dispositivo: str = "Ordenador") -> Tuple[bool, str, dict, dict]:
    """
    Intenta iniciar sesión en el servidor.
    Devuelve (éxito, mensaje_error, sesion, hogar_info)
    """
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password, "dispositivo": dispositivo},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            sesion = {
                "email":        data["email"],
                "nombre":       data["nombre"],
                "rol":          data["rol"],
                "is_premium":   data.get("is_premium", False),
                "hogar_nombre": data.get("hogar_nombre", "Hogar Principal")
            }
            hogar_info = {
                "hogar_estado": data.get("hogar_estado", "ok"),
                "hogar_ip":     data.get("hogar_ip", ""),
                "hogar_nombre": data.get("hogar_nombre", "Hogar Principal"),
                "ip_actual":    data.get("ip_actual", "")
            }
            _guardar_token(data["token"], sesion)
            return True, "", sesion, hogar_info
        return False, r.json().get("detail", "Error desconocido"), {}, {}
    except requests.exceptions.ConnectionError:
        return False, "Sin conexión al servidor KernossAI. Comprueba tu conexión a internet.", {}, {}
    except Exception as e:
        return False, str(e), {}, {}


def registro(nombre: str, email: str, password: str, rol: str = "Alumno", dispositivo: str = "Ordenador") -> Tuple[bool, str, dict]:
    """
    Registra un usuario nuevo en la base de datos de KernossAI.
    Devuelve (éxito, mensaje_error, sesion)
    """
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/registro",
            json={"nombre": nombre, "email": email, "password": password, "rol": rol, "dispositivo": dispositivo},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            sesion = {
                "email":        data["email"],
                "nombre":       data["nombre"],
                "rol":          data["rol"],
                "is_premium":   data.get("is_premium", False),
                "hogar_nombre": data.get("hogar_nombre", "Hogar Principal")
            }
            _guardar_token(data["token"], sesion)
            return True, "", sesion
        return False, r.json().get("detail", "Error desconocido"), {}
    except requests.exceptions.ConnectionError:
        return False, "Sin conexión al servidor KernossAI.", {}
    except Exception as e:
        return False, str(e), {}


def actualizar_hogar_principal(hogar_nombre: str = "Hogar Principal de Estudio") -> Tuple[bool, str]:
    """Actualiza la red/ubicación actual como Hogar Principal en la cuenta."""
    token, _ = _leer_token()
    if not token:
        return False, "No hay sesión activa."
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/hogar/actualizar",
            json={"hogar_nombre": hogar_nombre, "motivo": "Confirmado por el usuario"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, r.json().get("mensaje", "Hogar actualizado con éxito.")
        return False, r.json().get("detail", "No se pudo actualizar el hogar.")
    except Exception as e:
        return False, str(e)


# ── Sincronización de Chats en la Nube ───────────────────────

def obtener_chats_cloud() -> dict:
    """Descarga todas las conversaciones del usuario desde el servidor."""
    token, _ = _leer_token()
    if not token:
        return {}
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/chats",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json().get("chats", {})
    except Exception:
        pass
    return {}


def guardar_chat_cloud(chat_id: str, titulo: str, mensajes: list) -> bool:
    """Guarda o actualiza una conversación en la nube de forma asíncrona."""
    token, _ = _leer_token()
    if not token:
        return False
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/chats",
            json={"chat_id": chat_id, "titulo": titulo, "mensajes": mensajes},
            headers={"Authorization": f"Bearer {token}"},
            timeout=12
        )
        return r.status_code == 200
    except Exception:
        return False


def borrar_chat_cloud(chat_id: str) -> bool:
    """Elimina una conversación de la nube."""
    token, _ = _leer_token()
    if not token:
        return False
    try:
        r = requests.delete(
            f"{BACKEND_URL}/api/chats/{chat_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        return r.status_code == 200
    except Exception:
        return False


# ── Llamada a la IA (Proxy Seguro) ─────────────────────────

def consultar_ia(prompt: str, modelo: str = "groq") -> str:
    """
    Usa el token JWT guardado.
    Las claves API nunca salen del servidor.
    """
    token, _ = _leer_token()
    if not token:
        return "Error: no hay sesión activa. Inicia sesión primero."

    try:
        r = requests.post(
            f"{BACKEND_URL}/api/evaluar",
            json={"prompt": prompt, "model": modelo},
            headers={"Authorization": f"Bearer {token}"},
            timeout=60
        )
        if r.status_code == 200:
            return r.json().get("resultado", "Sin respuesta.")
        if r.status_code == 401:
            borrar_token()
            return "Sesión expirada o iniciada en otro dispositivo. Vuelve a iniciar sesión."
        return f"Error ({r.status_code}): {r.json().get('detail', r.text)}"
    except requests.exceptions.ConnectionError:
        return "Error de conexión. Comprueba tu internet."
    except Exception as e:
        return f"Error: {e}"


def llamar_gemini(prompt: str) -> str:
    return consultar_ia(prompt, modelo="gemini")


def llamar_groq(prompt: str) -> str:
    return consultar_ia(prompt, modelo="groq")