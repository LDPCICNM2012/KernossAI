import json
import os
import requests
 
BACKEND_URL = "https://kernosai-backend.onrender.com"
RUTA_TOKEN  = os.path.expanduser("~/.kernos_token.json")

# ── Guardar / leer token en disco ──────────────────
 
def _guardar_token(token: str, sesion: dict):
    with open(RUTA_TOKEN, "w", encoding="utf-8") as f:
        json.dump({"token": token, "sesion": sesion}, f)
 
def _leer_token() -> tuple[str, dict]:
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
        os.remove(RUTA_TOKEN)
 
def token_guardado() -> tuple[str, dict]:
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
            return token, sesion
    except Exception:
        pass
    return "", {}
 
 
# ── Login / Registro ────────────────────────────────
 
def login(email: str, password: str) -> tuple[bool, str, dict]:
    """
    Intenta iniciar sesión.
    Devuelve (éxito, mensaje_error, sesion)
    """
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=15
        )
        if r.status_code == 200:
            data   = r.json()
            sesion = {"email": data["email"], "nombre": data["nombre"], "rol": data["rol"]}
            _guardar_token(data["token"], sesion)
            return True, "", sesion
        return False, r.json().get("detail", "Error desconocido"), {}
    except requests.exceptions.ConnectionError:
        return False, "Sin conexión al servidor. Comprueba tu internet.", {}
    except Exception as e:
        return False, str(e), {}
 
 
def registro(nombre: str, email: str, password: str, rol: str) -> tuple[bool, str, dict]:
    """
    Registra un usuario nuevo.
    Devuelve (éxito, mensaje_error, sesion)
    """
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/registro",
            json={"nombre": nombre, "email": email, "password": password, "rol": rol},
            timeout=15
        )
        if r.status_code == 200:
            data   = r.json()
            sesion = {"email": data["email"], "nombre": data["nombre"], "rol": data["rol"]}
            _guardar_token(data["token"], sesion)
            return True, "", sesion
        return False, r.json().get("detail", "Error desconocido"), {}
    except requests.exceptions.ConnectionError:
        return False, "Sin conexión al servidor.", {}
    except Exception as e:
        return False, str(e), {}
 
 
# ── Llamada a la IA ─────────────────────────────────
 
def consultar_ia(prompt: str, modelo: str = "groq") -> str:
    """
    Sustituye a consultar_ia_backend() de tu main.py anterior.
    Usa el token JWT guardado — sin APP_SECRET en ningún lado.
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
            return "Sesión expirada. Vuelve a iniciar sesión."
        return f"Error ({r.status_code}): {r.json().get('detail', r.text)}"
    except requests.exceptions.ConnectionError:
        return "Error de conexión. Comprueba tu internet."
    except Exception as e:
        return f"Error: {e}"
 
 
# Shortcuts para mantener compatibilidad con tu código actual
def llamar_gemini(prompt: str) -> str:
    return consultar_ia(prompt, modelo="gemini")
 
def llamar_groq(prompt: str) -> str:
    return consultar_ia(prompt, modelo="groq")