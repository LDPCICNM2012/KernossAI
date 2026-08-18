import json
import os
import sys
import uuid
import hashlib
import hmac
import platform
import requests
from typing import Tuple, Dict, Any, Optional, List
from datetime import datetime

BACKEND_URL = "https://kernosai-backend.onrender.com"
RUTA_TOKEN  = os.path.expanduser("~/.kernos_token.json")
SOPORTE_EMAIL = "kernossai@support.com"
CLAVE_MAESTRA_SOPORTE = "KERNOS_SECURE_E2EE_SUPPORT_KEY_2026_V16"

# ── Generador de Identificador Único de Hardware (HWID) ────

def obtener_hwid() -> str:
    """
    Genera un identificador único y persistente del hardware físico del ordenador.
    Permite aplicar Hardware-Bans que persisten aunque se desinstale la app.
    """
    try:
        nodo_mac = str(uuid.getnode())
        sistema = platform.system()
        procesador = platform.processor() or platform.machine()
        nombre_equipo = platform.node()
        usuario_so = os.getenv("USERNAME") or os.getenv("USER") or "desconocido"
        
        huella_raw = f"{nodo_mac}_{sistema}_{procesador}_{nombre_equipo}_{usuario_so}"
        return hashlib.sha256(huella_raw.encode("utf-8")).hexdigest()[:32]
    except Exception:
        return hashlib.sha256(b"HWID_FALLBACK_DEVICE").hexdigest()[:32]


# ── Motor Criptográfico de Extremo a Extremo (E2EE) ───────

def _derivar_claves(passphrase: str, salt: bytes, length: int) -> bytes:
    """Deriva una corriente de claves de alta seguridad con PBKDF2-HMAC-SHA256 (100.000 iteraciones)."""
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, 100000, dklen=length)


def cifrar_e2ee(texto_plano: str, clave_secreta: str) -> str:
    """
    Cifra un mensaje localmente con Cifrado Autenticado E2EE (PBKDF2 + Stream Cipher + HMAC-SHA256).
    El servidor solo almacena el texto cifrado inaccesible.
    """
    if not texto_plano:
        return ""
    try:
        salt = os.urandom(16)
        iv   = os.urandom(16)
        datos = texto_plano.encode("utf-8")
        n = len(datos)

        # Derivar clave para cifrado + clave para autenticación HMAC
        keystream = _derivar_claves(clave_secreta, salt + iv, n + 32)
        key_enc = keystream[:n]
        key_mac = keystream[n:n + 32]

        # Cifrado XOR por flujo
        ciphertext = bytes(a ^ b for a, b in zip(datos, key_enc))

        # Tag de integridad HMAC-SHA256
        tag = hmac.new(key_mac, ciphertext, hashlib.sha256).digest()

        return f"E2EE:v1:{salt.hex()}:{iv.hex()}:{tag.hex()}:{ciphertext.hex()}"
    except Exception as e:
        return f"ERROR_CIFRADO:{e}"


def descifrar_e2ee(paquete_cifrado: str, clave_secreta: str) -> str:
    """Descifra localmente un mensaje E2EE recibido del servidor."""
    if not paquete_cifrado or not paquete_cifrado.startswith("E2EE:v1:"):
        return paquete_cifrado  # No cifrado o texto plano legado
    try:
        partes = paquete_cifrado.split(":")
        if len(partes) != 6:
            return "[Mensaje cifrado con formato no reconocido]"

        _, _, salt_hex, iv_hex, tag_hex, cipher_hex = partes
        salt = bytes.fromhex(salt_hex)
        iv   = bytes.fromhex(iv_hex)
        tag_esperado = bytes.fromhex(tag_hex)
        ciphertext = bytes.fromhex(cipher_hex)
        n = len(ciphertext)

        keystream = _derivar_claves(clave_secreta, salt + iv, n + 32)
        key_enc = keystream[:n]
        key_mac = keystream[n:n + 32]

        tag_calculado = hmac.new(key_mac, ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(tag_esperado, tag_calculado):
            return "[Error: El mensaje ha sido alterado o la clave de descifrado es incorrecta]"

        plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_enc))
        return plaintext.decode("utf-8")
    except Exception:
        return "[Mensaje cifrado confidencial]"


def _obtener_clave_canal(user_a: str, user_b: str) -> str:
    """Genera la clave de cifrado compartida para una conversación P2P o Soporte."""
    part = sorted([user_a.strip().lower(), user_b.strip().lower()])
    if SOPORTE_EMAIL in part:
        return f"{CLAVE_MAESTRA_SOPORTE}::{part[0]}::{part[1]}"
    return f"KERNOS_E2EE_PAIR::{part[0]}::{part[1]}::SALT_2026"


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
        elif r.status_code in (401, 403):
            # El servidor invalidó la sesión o el token es antiguo -> limpiar
            borrar_token()
            return "", {}
    except requests.exceptions.ConnectionError:
        # Modo offline si no hay conexión
        if sesion and sesion.get("email"):
            return token, sesion
    except Exception:
        pass
    return "", {}


# ── Login / Registro con Detección de HWID & Hogar ─────────

def login(email: str, password: str, dispositivo: str = "Ordenador") -> Tuple[bool, str, dict, dict]:
    try:
        hwid = obtener_hwid()
        r = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password, "dispositivo": dispositivo, "hwid": hwid},
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
    try:
        hwid = obtener_hwid()
        r = requests.post(
            f"{BACKEND_URL}/auth/registro",
            json={"nombre": nombre, "email": email, "password": password, "rol": rol, "dispositivo": dispositivo, "hwid": hwid},
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
    token, _ = _leer_token()
    if not token:
        return False, "No hay sesión activa."
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/actualizar_hogar",
            json={"hogar_nombre": hogar_nombre, "motivo": "Confirmado por el usuario"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, r.json().get("mensaje", "Hogar actualizado con éxito.")
        return False, r.json().get("detail", "No se pudo actualizar el hogar.")
    except Exception as e:
        return False, str(e)


# ── Mensajería Privada E2EE & Soporte Oficial ─────────────

def enviar_mensaje_soporte(texto: str) -> Tuple[bool, str]:
    """Cifra el mensaje con E2EE y lo envía al canal oficial de soporte."""
    token, sesion = _leer_token()
    if not token:
        return False, "Inicia sesión para escribir a soporte."
    
    mi_email = sesion.get("email", "")
    clave = _obtener_clave_canal(mi_email, SOPORTE_EMAIL)
    cifrado = cifrar_e2ee(texto, clave)

    try:
        r = requests.post(
            f"{BACKEND_URL}/api/mensajes/enviar",
            json={"destinatario": SOPORTE_EMAIL, "texto_cifrado": cifrado, "tipo": "soporte"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, "Mensaje enviado a Soporte con cifrado E2EE."
        return False, r.json().get("detail", "Error al enviar mensaje.")
    except Exception as e:
        return False, str(e)


def obtener_mensajes_soporte() -> Tuple[bool, List[dict]]:
    """Descarga los mensajes cifrados de soporte y los descifra localmente."""
    token, sesion = _leer_token()
    if not token:
        return False, []
    
    mi_email = sesion.get("email", "")
    clave = _obtener_clave_canal(mi_email, SOPORTE_EMAIL)

    try:
        r = requests.get(
            f"{BACKEND_URL}/api/mensajes/soporte",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            hilo = r.json().get("hilo", {})
            mensajes_raw = hilo.get("mensajes", [])
            mensajes_descifrados = []
            for m in mensajes_raw:
                texto_claro = descifrar_e2ee(m.get("texto_cifrado", ""), clave)
                mensajes_descifrados.append({
                    "id": m.get("id"),
                    "emisor_email": m.get("emisor_email"),
                    "emisor_nombre": m.get("emisor_nombre"),
                    "emisor_rol": m.get("emisor_rol"),
                    "destinatario_email": m.get("destinatario_email"),
                    "texto": texto_claro,
                    "timestamp": m.get("timestamp"),
                    "es_mio": m.get("emisor_email", "").lower() == mi_email.lower()
                })
            return True, mensajes_descifrados
        return False, []
    except Exception:
        return False, []


def enviar_mensaje_p2p(destinatario_email: str, texto: str) -> Tuple[bool, str]:
    """Cifra el mensaje con la clave privada de ambos alumnos y lo envía."""
    token, sesion = _leer_token()
    if not token:
        return False, "Inicia sesión para enviar mensajes."
    
    mi_email = sesion.get("email", "")
    clave = _obtener_clave_canal(mi_email, destinatario_email)
    cifrado = cifrar_e2ee(texto, clave)

    try:
        r = requests.post(
            f"{BACKEND_URL}/api/mensajes/enviar",
            json={"destinatario": destinatario_email, "texto_cifrado": cifrado, "tipo": "p2p"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, "Mensaje enviado con cifrado E2EE."
        return False, r.json().get("detail", "Error al enviar mensaje.")
    except Exception as e:
        return False, str(e)


def obtener_chat_p2p(contacto_email: str) -> Tuple[bool, List[dict]]:
    """Descarga y descifra los mensajes del chat entre el usuario y otro alumno."""
    token, sesion = _leer_token()
    if not token:
        return False, []
    
    mi_email = sesion.get("email", "")
    clave = _obtener_clave_canal(mi_email, contacto_email)

    try:
        r = requests.get(
            f"{BACKEND_URL}/api/mensajes/chat/{contacto_email}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            hilo = r.json().get("hilo", {})
            mensajes_raw = hilo.get("mensajes", [])
            mensajes_descifrados = []
            for m in mensajes_raw:
                texto_claro = descifrar_e2ee(m.get("texto_cifrado", ""), clave)
                mensajes_descifrados.append({
                    "id": m.get("id"),
                    "emisor_email": m.get("emisor_email"),
                    "emisor_nombre": m.get("emisor_nombre"),
                    "emisor_rol": m.get("emisor_rol"),
                    "destinatario_email": m.get("destinatario_email"),
                    "texto": texto_claro,
                    "timestamp": m.get("timestamp"),
                    "es_mio": m.get("emisor_email", "").lower() == mi_email.lower()
                })
            return True, mensajes_descifrados
        return False, []
    except Exception:
        return False, []


def listar_conversaciones() -> Tuple[bool, List[dict]]:
    token, _ = _leer_token()
    if not token:
        return False, []
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/mensajes/conversaciones",
            headers={"Authorization": f"Bearer {token}"},
            timeout=12
        )
        if r.status_code == 200:
            return True, r.json().get("conversaciones", [])
        return False, []
    except Exception:
        return False, []


def buscar_usuarios(query: str) -> List[dict]:
    token, _ = _leer_token()
    if not token:
        return []
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/mensajes/buscar_usuario?q={query}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json().get("resultados", [])
        return []
    except Exception:
        return []


# ── Funciones de Administración & Moderación (Bans) ───────

def admin_listar_usuarios() -> Tuple[bool, List[dict]]:
    """Obtiene la lista completa de usuarios con IP y HWID (Solo admin)."""
    token, _ = _leer_token()
    if not token:
        return False, []
    try:
        r = requests.get(
            f"{BACKEND_URL}/admin/usuarios",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, r.json().get("usuarios", [])
        return False, []
    except Exception:
        return False, []


def admin_aplicar_ban(objetivo: str, tipo: str = "usuario", motivo: str = "Infracción de normas") -> Tuple[bool, str]:
    """Aplica baneo de usuario, IP o Hardware (HWID)."""
    token, _ = _leer_token()
    if not token:
        return False, "Sin sesión admin."
    try:
        r = requests.post(
            f"{BACKEND_URL}/admin/ban",
            json={"objetivo": objetivo, "tipo": tipo, "motivo": motivo},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, r.json().get("mensaje", "Baneo aplicado.")
        return False, r.json().get("detail", "Error al aplicar baneo.")
    except Exception as e:
        return False, str(e)


def admin_desbanear(objetivo: str, tipo: str = "usuario") -> Tuple[bool, str]:
    """Desbanea un usuario, IP o Hardware (HWID)."""
    token, _ = _leer_token()
    if not token:
        return False, "Sin sesión admin."
    try:
        r = requests.post(
            f"{BACKEND_URL}/admin/desbanear",
            json={"objetivo": objetivo, "tipo": tipo},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, r.json().get("mensaje", "Desbaneo completado.")
        return False, r.json().get("detail", "Error al desbanear.")
    except Exception as e:
        return False, str(e)


def admin_ver_mensajes_raw() -> Tuple[bool, dict]:
    """Descarga la base de datos de mensajes cifrados en bruto para verificar el cifrado E2EE."""
    token, _ = _leer_token()
    if not token:
        return False, {}
    try:
        r = requests.get(
            f"{BACKEND_URL}/admin/mensajes_raw",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if r.status_code == 200:
            return True, r.json()
        return False, {}
    except Exception:
        return False, {}


# ── Sincronización de Chats IA en la Nube ─────────────────

def obtener_chats_cloud() -> dict:
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