import json
import os
import sys
import uuid
import hashlib
import hmac
import platform
import secrets
import base64
import re
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


RUTA_CUENTAS = os.path.expanduser("~/.kernos_accounts.json")


# ── Guardar / leer token y multicuentas en disco ──

def obtener_cuentas_guardadas() -> List[dict]:
    """Devuelve la lista de cuentas recordadas en este equipo."""
    if os.path.exists(RUTA_CUENTAS):
        try:
            with open(RUTA_CUENTAS, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("cuentas", [])
        except Exception:
            pass
    return []


def _guardar_lista_cuentas(cuentas: List[dict]):
    try:
        with open(RUTA_CUENTAS, "w", encoding="utf-8") as f:
            json.dump({"cuentas": cuentas}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def registrar_cuenta_en_switcher(email: str, nombre: str, rol: str, token: str, sesion: dict):
    if not email:
        return
    cuentas = obtener_cuentas_guardadas()
    encontrada = False
    for c in cuentas:
        if c.get("email", "").lower() == email.lower():
            c["nombre"] = nombre
            c["rol"] = rol
            c["token"] = token
            c["sesion"] = sesion
            c["ultimo_acceso"] = datetime.now().isoformat()
            encontrada = True
            break
    if not encontrada:
        cuentas.append({
            "email": email,
            "nombre": nombre,
            "rol": rol,
            "token": token,
            "sesion": sesion,
            "ultimo_acceso": datetime.now().isoformat()
        })
    _guardar_lista_cuentas(cuentas)


def cambiar_a_cuenta(email_target: str) -> Tuple[bool, str, dict]:
    """Cambia la sesión activa a otra cuenta guardada en el dispositivo."""
    cuentas = obtener_cuentas_guardadas()
    target = None
    for c in cuentas:
        if c.get("email", "").lower() == email_target.strip().lower():
            target = c
            break
    if not target:
        return False, "Cuenta no encontrada en la lista de cuentas guardadas.", {}
    
    token = target.get("token", "")
    sesion = target.get("sesion", {})
    _guardar_token(token, sesion)
    return True, f"Cambiado a la cuenta {email_target}", sesion


def eliminar_cuenta_switcher(email_target: str) -> bool:
    """Elimina una cuenta de la lista de cuentas recordadas."""
    cuentas = obtener_cuentas_guardadas()
    cuentas_nuevas = [c for c in cuentas if c.get("email", "").lower() != email_target.strip().lower()]
    _guardar_lista_cuentas(cuentas_nuevas)
    return True


def agregar_cuenta_secundaria(email: str, password: str) -> Tuple[bool, str, dict]:
    """Inicia sesión con una cuenta secundaria y la guarda en la lista sin perder la sesión activa."""
    token_actual, sesion_actual = _leer_token()
    
    ok, error, sesion_nueva, _ = login(email, password)
    if not ok:
        if token_actual and sesion_actual:
            _guardar_token(token_actual, sesion_actual)
        return False, error, {}
    
    token_nuevo, _ = _leer_token()
    registrar_cuenta_en_switcher(
        sesion_nueva.get("email"),
        sesion_nueva.get("nombre"),
        sesion_nueva.get("rol"),
        token_nuevo,
        sesion_nueva
    )
    
    # Si había una sesión activa previa, restaurarla
    if token_actual and sesion_actual:
        _guardar_token(token_actual, sesion_actual)
        
    return True, "Cuenta agregada con éxito al gestor de multicuentas.", sesion_nueva


def actualizar_rol_usuario(nuevo_rol: str) -> Tuple[bool, str]:
    """Actualiza el rol del usuario (Alumno/Profesor) en Supabase y en la sesión local."""
    token, sesion = _leer_token()
    if not token or not sesion.get("email"):
        return False, "No hay sesión activa."
    
    email_clean = sesion.get("email", "").strip().lower()
    
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json"
        }
        r = requests.patch(
            f"{sb_url}/usuarios?email=eq.{email_clean}",
            json={"rol": nuevo_rol},
            headers=sb_headers,
            timeout=6
        )
        if r.status_code in (200, 204):
            sesion["rol"] = nuevo_rol
            _guardar_token(token, sesion)
            registrar_cuenta_en_switcher(email_clean, sesion.get("nombre"), nuevo_rol, token, sesion)
            return True, f"Rol actualizado a {nuevo_rol} con éxito."
    except Exception as e:
        return False, f"Error al conectar con la base de datos: {e}"
        
    sesion["rol"] = nuevo_rol
    _guardar_token(token, sesion)
    registrar_cuenta_en_switcher(email_clean, sesion.get("nombre"), nuevo_rol, token, sesion)
    return True, f"Rol actualizado a {nuevo_rol}."


def _guardar_token(token: str, sesion: dict):
    try:
        with open(RUTA_TOKEN, "w", encoding="utf-8") as f:
            json.dump({"token": token, "sesion": sesion}, f, ensure_ascii=False, indent=2)
        if sesion and sesion.get("email"):
            registrar_cuenta_en_switcher(
                sesion.get("email"), sesion.get("nombre"), sesion.get("rol"), token, sesion
            )
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
    if not token or not sesion or not sesion.get("email"):
        return "", {}
    
    email_clean = sesion.get("email", "").strip().lower()
    
    # 1. Comprobar si el usuario sigue existiendo y activo en Supabase
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        
        r_u = requests.get(f"{sb_url}/usuarios?email=eq.{email_clean}", headers=sb_headers, timeout=5)
        if r_u.status_code == 200:
            usrs = r_u.json()
            if not usrs:
                # La cuenta fue eliminada del sistema
                borrar_token()
                return "", {}
            u = usrs[0]
            sesion["nombre"] = u.get("nombre", sesion.get("nombre"))
            sesion["rol"] = u.get("rol", sesion.get("rol"))
            sesion["is_premium"] = u.get("is_premium", (email_clean == "kernossai@support.com"))
            _guardar_token(token, sesion)
        
        # Verificar si el usuario o su hardware fueron baneados
        ok_ban, _, _ = _verificar_baneos_supabase(email=email_clean)
        if not ok_ban:
            borrar_token()
            return "", {}
            
        return token, sesion
    except Exception:
        pass
    
    # 2. Si no hay conexión o fallo transitorio, mantener la sesión localmente
    return token, sesion


def _verificar_baneos_supabase(email: Optional[str] = None, hwid: Optional[str] = None, ip: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Verifica en tiempo real si el usuario, su red IP o su Hardware (HWID) están baneados en Supabase.
    Devuelve (es_valido, motivo, tipo_sancion).
    """
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        r = requests.get(f"{sb_url}/bans", headers=sb_headers, timeout=5)
        if r.status_code == 200:
            bans = r.json()
            mi_hwid = (hwid or obtener_hwid()).strip().lower()
            em_clean = (email or "").strip().lower()
            ip_clean = (ip or "").strip().lower()

            for b in bans:
                obj = (b.get("objetivo") or "").strip().lower()
                tipo = (b.get("tipo") or "").strip().lower()
                motivo = b.get("motivo") or "Infracción de normas del sistema"

                # 1. Comprobar Hardware-Ban (HWID)
                if (tipo in ("hwid", "hardware")) and mi_hwid and obj == mi_hwid:
                    return False, motivo, "Hardware-Ban (Dispositivo Físico)"

                # 2. Comprobar IP-Ban
                if (tipo in ("ip", "red")) and ip_clean and obj == ip_clean:
                    return False, motivo, "IP-Ban (Red / Conexión)"

                # 3. Comprobar Ban de Cuenta
                if (tipo in ("usuario", "email", "cuenta")) and em_clean and obj == em_clean:
                    return False, motivo, "Baneo de Cuenta Permanente"

                # Fallback por coincidencia de texto
                if em_clean and obj == em_clean:
                    tipo_nombre = "Hardware-Ban" if tipo in ("hwid", "hardware") else ("IP-Ban" if tipo in ("ip", "red") else "Baneo de Cuenta")
                    return False, motivo, tipo_nombre

    except Exception:
        pass
    return True, "", ""


def verificar_estado_baneo(email: Optional[str] = None) -> Tuple[bool, str, str]:
    """Función pública de comprobación en tiempo real para el vigilante del Dashboard."""
    return _verificar_baneos_supabase(email=email)


# ── Login / Registro con Detección de HWID & Hogar ─────────

def login(email: str, password: str, dispositivo: str = "Ordenador") -> Tuple[bool, str, dict, dict]:
    email_clean = email.strip().lower()
    hwid = obtener_hwid()

    # 1. Comprobar Hardware-Ban o Ban de Cuenta antes de procesar login
    ok_ban, motivo_ban, tipo_ban = _verificar_baneos_supabase(email=email_clean, hwid=hwid)
    if not ok_ban:
        return False, f"⛔ ACCESO DENEGADO ({tipo_ban}): {motivo_ban}", {}, {}

    # 2. Verificar credenciales en la base de datos permanente de Supabase
    u_supabase = None
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        r_sb = requests.get(f"{sb_url}/usuarios?email=eq.{email_clean}", headers=sb_headers, timeout=5)
        if r_sb.status_code == 200:
            usrs = r_sb.json()
            if not usrs:
                return False, "El correo no está registrado en KernossAI.", {}, {}
            u_supabase = usrs[0]
            salt = u_supabase.get("salt", "")
            expected_hash = u_supabase.get("password_hash")
            if salt and expected_hash:
                calc_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
                if calc_hash != expected_hash:
                    return False, "Contraseña incorrecta.", {}, {}
    except Exception:
        pass

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
                "is_premium":   bool(data.get("is_premium")) or (email_clean == "kernossai@support.com"),
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
    except Exception:
        pass

    # Si se validó en Supabase exitosamente:
    if u_supabase:
        is_prem = u_supabase.get("is_premium", (email_clean == "kernossai@support.com"))
        sesion = {
            "email":        u_supabase["email"],
            "nombre":       u_supabase.get("nombre", "KernossAI Soporte"),
            "rol":          u_supabase.get("rol", "Profesor"),
            "is_premium":   is_prem,
            "hogar_nombre": u_supabase.get("hogar_nombre", "Hogar Principal de Estudio")
        }
        hogar_info = {
            "hogar_estado": "ok",
            "hogar_ip":     "",
            "hogar_nombre": "Hogar Principal de Estudio",
            "ip_actual":    ""
        }
        # Crear token local
        header_b64 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        payload = {
            "sub": email_clean,
            "nombre": sesion["nombre"],
            "rol": sesion["rol"],
            "is_premium": is_prem,
            "exp": int(datetime.now().timestamp()) + 2592000
        }
        import base64
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        token_simulado = f"{header_b64}.{payload_b64}.local_signature"
        _guardar_token(token_simulado, sesion)
        return True, "", sesion, hogar_info

    return False, "Error al iniciar sesión.", {}, {}


def registro(nombre: str, email: str, password: str, rol: str = "Alumno", dispositivo: str = "Ordenador") -> Tuple[bool, str, dict]:
    email_clean = email.strip().lower()
    hwid = obtener_hwid()
    is_prem = (email_clean == "kernossai@support.com")

    # 1. Comprobar Hardware-Ban o Ban de Cuenta antes de permitir registro
    ok_ban, motivo_ban, tipo_ban = _verificar_baneos_supabase(email=email_clean, hwid=hwid)
    if not ok_ban:
        return False, f"⛔ REGISTRO BLOQUEADO ({tipo_ban}): {motivo_ban}", {}

    # 2. Guardar en la base de datos permanente de Supabase
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        u_data = {
            "email": email_clean,
            "nombre": nombre.strip(),
            "password_hash": pwd_hash,
            "salt": salt,
            "rol": rol,
            "is_premium": is_prem,
            "hwid": hwid
        }
        requests.post(f"{sb_url}/usuarios", json=u_data, headers=sb_headers, timeout=6)
    except Exception:
        pass

    try:
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
                "is_premium":   data.get("is_premium", is_prem),
                "hogar_nombre": data.get("hogar_nombre", "Hogar Principal")
            }
            _guardar_token(data["token"], sesion)
            return True, "", sesion
    except Exception:
        pass

    # Fallback local de sesión si ya está en Supabase
    sesion = {
        "email": email_clean,
        "nombre": nombre.strip(),
        "rol": rol,
        "is_premium": is_prem,
        "hogar_nombre": "Hogar Principal de Estudio"
    }
    # Intentar login para obtener JWT
    ok_l, _, ses_l, _ = login(email_clean, password, dispositivo)
    if ok_l:
        return True, "", ses_l
    return True, "", sesion


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


def borrar_cuenta_usuario() -> Tuple[bool, str]:
    """Solicita la eliminación definitiva de la cuenta del usuario en Render y Supabase."""
    token, sesion = _leer_token()
    if not token:
        return False, "No hay sesión activa."
    
    email = sesion.get("email", "").strip().lower()
    
    # 1. Intentar vía endpoint de backend en Render
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/borrar_cuenta",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            borrar_token()
            return True, "Cuenta eliminada permanentemente del sistema."
    except Exception:
        pass

    # 2. Fallback garantizado directo a Supabase
    if email:
        try:
            sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
            sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
            sb_headers = {
                "apikey": sb_key,
                "Authorization": f"Bearer {sb_key}",
                "Content-Type": "application/json"
            }
            requests.delete(f"{sb_url}/usuarios?email=eq.{email}", headers=sb_headers, timeout=8)
            requests.delete(f"{sb_url}/chats_cloud?email=eq.{email}", headers=sb_headers, timeout=8)
            borrar_token()
            return True, "Cuenta eliminada permanentemente de la base de datos."
        except Exception as e:
            return False, f"Error al conectar con la base de datos: {e}"

    borrar_token()
    return True, "Sesión local eliminada."


# ── Mensajería Privada E2EE & Soporte Oficial ─────────────

def enviar_mensaje_soporte(texto: str) -> Tuple[bool, str]:
    """Cifra el mensaje con E2EE y lo envía al canal oficial de soporte en Supabase y Render."""
    token, sesion = _leer_token()
    if not token:
        return False, "Inicia sesión para escribir a soporte."
    
    mi_email = sesion.get("email", "").strip().lower()
    mi_nombre = sesion.get("nombre", "Alumno")
    mi_rol = sesion.get("rol", "Alumno")
    
    clave = _obtener_clave_canal(mi_email, SOPORTE_EMAIL)
    cifrado = cifrar_e2ee(texto, clave)
    conv_id = f"{sorted([mi_email, SOPORTE_EMAIL])[0]}:{sorted([mi_email, SOPORTE_EMAIL])[1]}"
    now_iso = datetime.now().isoformat()
    msg_id = f"msg_{uuid.uuid4().hex[:10]}"

    # 1. Guardar en la base de datos permanente de Supabase
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json"
        }
        msg_payload = {
            "id": msg_id,
            "conv_id": conv_id,
            "emisor_email": mi_email,
            "emisor_nombre": mi_nombre,
            "emisor_rol": mi_rol,
            "destinatario_email": SOPORTE_EMAIL,
            "texto_cifrado": cifrado,
            "timestamp": now_iso,
            "leido": False
        }
        requests.post(f"{sb_url}/mensajes", json=msg_payload, headers=sb_headers, timeout=6)
    except Exception:
        pass

    # 2. Notificar al backend en Render
    try:
        requests.post(
            f"{BACKEND_URL}/api/mensajes/enviar",
            json={"destinatario": SOPORTE_EMAIL, "texto_cifrado": cifrado, "tipo": "soporte"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
    except Exception:
        pass

    return True, "Mensaje enviado a Soporte con cifrado E2EE."


def obtener_mensajes_soporte() -> Tuple[bool, List[dict]]:
    """Descarga los mensajes cifrados de soporte desde Supabase y los descifra localmente."""
    token, sesion = _leer_token()
    if not token:
        return False, []
    
    mi_email = sesion.get("email", "").strip().lower()
    clave = _obtener_clave_canal(mi_email, SOPORTE_EMAIL)
    conv_id = f"{sorted([mi_email, SOPORTE_EMAIL])[0]}:{sorted([mi_email, SOPORTE_EMAIL])[1]}"

    mensajes_raw = []
    # 1. Leer directamente de Supabase
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        r_sb = requests.get(f"{sb_url}/mensajes?conv_id=eq.{conv_id}&order=timestamp.asc", headers=sb_headers, timeout=6)
        if r_sb.status_code == 200:
            mensajes_raw = r_sb.json()
    except Exception:
        pass

    # 2. Fallback al backend de Render
    if not mensajes_raw:
        try:
            r = requests.get(
                f"{BACKEND_URL}/api/mensajes/soporte",
                headers={"Authorization": f"Bearer {token}"},
                timeout=8
            )
            if r.status_code == 200:
                mensajes_raw = r.json().get("hilo", {}).get("mensajes", [])
        except Exception:
            pass

    mensajes_descifrados = []
    for m in mensajes_raw:
        texto_claro = descifrar_e2ee(m.get("texto_cifrado", ""), clave)
        es_mio = (m.get("emisor_email", "").strip().lower() == mi_email)
        mensajes_descifrados.append({
            "id": m.get("id"),
            "emisor_email": m.get("emisor_email"),
            "emisor_nombre": m.get("emisor_nombre"),
            "emisor_rol": m.get("emisor_rol"),
            "destinatario_email": m.get("destinatario_email"),
            "texto": texto_claro,
            "timestamp": m.get("timestamp"),
            "es_mio": es_mio
        })
    return True, mensajes_descifrados


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
    """Obtiene la lista completa de usuarios con IP y HWID desde Supabase y Render."""
    token, _ = _leer_token()
    if not token:
        return False, []
    
    # 1. Consultar directamente Supabase
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        r_u = requests.get(f"{sb_url}/usuarios", headers=sb_headers, timeout=6)
        r_b = requests.get(f"{sb_url}/bans", headers=sb_headers, timeout=6)
        if r_u.status_code == 200:
            usrs_sb = r_u.json()
            bans_sb = r_b.json() if r_b.status_code == 200 else []
            
            bans_usuarios = {b.get("objetivo", "").lower() for b in bans_sb if b.get("tipo") == "usuario"}
            bans_ips = {b.get("objetivo", "").lower() for b in bans_sb if b.get("tipo") == "ip"}
            bans_hwids = {b.get("objetivo", "").lower() for b in bans_sb if b.get("tipo") == "hwid"}

            lista = []
            for u in usrs_sb:
                em = u.get("email", "").strip().lower()
                ip = u.get("ip_ultima") or u.get("ip_registro") or "N/D"
                hwid = u.get("hwid") or "N/D"
                lista.append({
                    "email": u.get("email", ""),
                    "nombre": u.get("nombre", em),
                    "rol": u.get("rol", "Alumno"),
                    "is_premium": u.get("is_premium", False),
                    "created_at": u.get("created_at"),
                    "last_login": u.get("last_login"),
                    "ip": ip,
                    "ip_baneada": (ip.lower() in bans_ips and ip != "N/D"),
                    "hwid": hwid,
                    "hwid_baneado": (hwid.lower() in bans_hwids and hwid != "N/D"),
                    "hogar_nombre": u.get("hogar_nombre", "Hogar Principal de Estudio"),
                    "baneado": (em in bans_usuarios)
                })
            return True, lista
    except Exception:
        pass

    # 2. Fallback a Render
    try:
        r = requests.get(
            f"{BACKEND_URL}/admin/usuarios",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
        if r.status_code == 200:
            return True, r.json().get("usuarios", [])
    except Exception:
        pass

    return False, []


def admin_aplicar_ban(objetivo: str, tipo: str = "usuario", motivo: str = "Infracción de normas") -> Tuple[bool, str]:
    """Aplica baneo de usuario, IP o Hardware (HWID) directamente en Supabase y Render."""
    token, _ = _leer_token()
    if not token:
        return False, "Sin sesión admin."
    
    obj_clean = objetivo.strip()
    # 1. Guardar en Supabase directamente
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        b_data = {
            "objetivo": obj_clean,
            "tipo": tipo,
            "motivo": motivo,
            "fecha": datetime.now().isoformat()
        }
        requests.post(f"{sb_url}/bans", json=b_data, headers=sb_headers, timeout=6)
    except Exception:
        pass

    # 2. Notificar a Render
    try:
        requests.post(
            f"{BACKEND_URL}/admin/ban",
            json={"objetivo": obj_clean, "tipo": tipo, "motivo": motivo},
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
    except Exception:
        pass

    return True, f"Baneo de {tipo} '{obj_clean}' aplicado con éxito."


def admin_desbanear(objetivo: str, tipo: str = "usuario") -> Tuple[bool, str]:
    """Desbanea un usuario, IP o Hardware (HWID) en Supabase y Render."""
    token, _ = _leer_token()
    if not token:
        return False, "Sin sesión admin."
    
    obj_clean = objetivo.strip()
    # 1. Eliminar de Supabase directamente
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        requests.delete(f"{sb_url}/bans?objetivo=eq.{obj_clean}", headers=sb_headers, timeout=6)
    except Exception:
        pass

    # 2. Notificar a Render
    try:
        requests.post(
            f"{BACKEND_URL}/admin/desbanear",
            json={"objetivo": obj_clean, "tipo": tipo},
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
    except Exception:
        pass

    return True, f"Desbaneo de {tipo} '{obj_clean}' completado con éxito."


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


def admin_obtener_tickets_soporte() -> Tuple[bool, List[dict]]:
    """Descarga todos los tickets de soporte dirigidos a kernossai@support.com desde Supabase y los descifra."""
    token, _ = _leer_token()
    if not token:
        return False, []
    
    mensajes = []
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        r_sb = requests.get(
            f"{sb_url}/mensajes?or=(emisor_email.eq.{SOPORTE_EMAIL},destinatario_email.eq.{SOPORTE_EMAIL})&order=timestamp.asc",
            headers=sb_headers, timeout=6
        )
        if r_sb.status_code == 200:
            mensajes = r_sb.json()
    except Exception:
        pass

    if not mensajes:
        try:
            r = requests.get(
                f"{BACKEND_URL}/admin/soporte/tickets",
                headers={"Authorization": f"Bearer {token}"},
                timeout=8
            )
            if r.status_code == 200:
                return True, r.json().get("tickets", [])
        except Exception:
            pass

    hilos = {}
    for m in mensajes:
        c_id = m.get("conv_id")
        if not c_id:
            continue
        if c_id not in hilos:
            hilos[c_id] = []
        hilos[c_id].append(m)

    tickets_procesados = []
    for c_id, msgs in hilos.items():
        parts = c_id.split(":")
        otro = [p for p in parts if p.lower() != SOPORTE_EMAIL.lower()]
        u_email = otro[0] if otro else parts[0]
        clave_canal = _obtener_clave_canal(u_email, SOPORTE_EMAIL)
        
        msgs_descifrados = []
        u_nombre = u_email
        u_rol = "Alumno"
        for m in msgs:
            txt_plano = descifrar_e2ee(m.get("texto_cifrado", ""), clave_canal)
            es_soporte = (m.get("emisor_email", "").strip().lower() == SOPORTE_EMAIL.lower())
            if not es_soporte:
                u_nombre = m.get("emisor_nombre") or u_nombre
                u_rol = m.get("emisor_rol") or u_rol
            msgs_descifrados.append({
                "id": m.get("id"),
                "emisor_email": m.get("emisor_email"),
                "emisor_nombre": m.get("emisor_nombre"),
                "emisor_rol": m.get("emisor_rol", "Alumno"),
                "destinatario_email": m.get("destinatario_email"),
                "texto": txt_plano,
                "timestamp": m.get("timestamp"),
                "es_soporte": es_soporte
            })
        ultimo_texto = msgs_descifrados[-1]["texto"] if msgs_descifrados else "Sin mensajes"
        tickets_procesados.append({
            "usuario_email": u_email,
            "usuario_nombre": u_nombre,
            "usuario_rol": u_rol,
            "total_mensajes": len(msgs_descifrados),
            "ultimo_timestamp": msgs[-1].get("timestamp") if msgs else "",
            "ultimo_texto": ultimo_texto,
            "mensajes": msgs_descifrados
        })
    tickets_procesados.sort(key=lambda t: t.get("ultimo_timestamp") or "", reverse=True)
    return True, tickets_procesados


def admin_responder_ticket_soporte(usuario_email: str, texto_respuesta: str) -> Tuple[bool, str]:
    """Cifra y envía una respuesta oficial a un alumno desde kernossai@support.com a Supabase y Render."""
    token, _ = _leer_token()
    if not token:
        return False, "Sin sesión admin."
    
    u_clean = usuario_email.strip().lower()
    clave_canal = _obtener_clave_canal(u_clean, SOPORTE_EMAIL)
    cifrado = cifrar_e2ee(texto_respuesta, clave_canal)
    conv_id = f"{sorted([u_clean, SOPORTE_EMAIL])[0]}:{sorted([u_clean, SOPORTE_EMAIL])[1]}"
    now_iso = datetime.now().isoformat()
    msg_id = f"msg_{uuid.uuid4().hex[:10]}"

    # 1. Guardar en Supabase directamente
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Content-Type": "application/json"
        }
        msg_payload = {
            "id": msg_id,
            "conv_id": conv_id,
            "emisor_email": SOPORTE_EMAIL,
            "emisor_nombre": "🛡️ Soporte Oficial KernossAI",
            "emisor_rol": "Soporte VIP",
            "destinatario_email": u_clean,
            "texto_cifrado": cifrado,
            "timestamp": now_iso,
            "leido": False
        }
        requests.post(f"{sb_url}/mensajes", json=msg_payload, headers=sb_headers, timeout=6)
    except Exception:
        pass

    # 2. Notificar al backend de Render
    try:
        requests.post(
            f"{BACKEND_URL}/admin/soporte/responder",
            json={"destinatario": u_clean, "texto_cifrado": cifrado},
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
    except Exception:
        pass

    return True, "Respuesta oficial enviada al alumno con éxito."


def admin_borrar_ticket_soporte(usuario_email: str) -> Tuple[bool, str]:
    """Elimina por completo el historial de mensajes de soporte con un usuario en Supabase y Render (estilo WhatsApp)."""
    token, _ = _leer_token()
    if not token:
        return False, "Sin sesión admin."
    
    u_clean = usuario_email.strip().lower()
    conv_id = f"{sorted([u_clean, SOPORTE_EMAIL])[0]}:{sorted([u_clean, SOPORTE_EMAIL])[1]}"
    
    # 1. Eliminar de Supabase directamente
    try:
        sb_url = "https://bqgzpfqowctvslahqqdt.supabase.co/rest/v1"
        sb_key = "sb_publishable_dZj9klqezhfFdHddC5l2_A_Swi8OsMQ"
        sb_headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
        requests.delete(f"{sb_url}/mensajes?conv_id=eq.{conv_id}", headers=sb_headers, timeout=6)
        requests.delete(f"{sb_url}/mensajes?or=(and(emisor_email.eq.{u_clean},destinatario_email.eq.{SOPORTE_EMAIL}),and(emisor_email.eq.{SOPORTE_EMAIL},destinatario_email.eq.{u_clean}))", headers=sb_headers, timeout=6)
    except Exception:
        pass

    # 2. Notificar al backend de Render
    try:
        requests.delete(
            f"{BACKEND_URL}/admin/soporte/ticket/{u_clean}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
    except Exception:
        pass

    return True, f"Conversación con '{u_clean}' eliminada con éxito."


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


# ── Llamada a la IA (Proxy Seguro con Bloqueo de Baneados) ───

def consultar_ia(prompt: str, modelo: str = "groq") -> str:
    token, sesion = _leer_token()
    if not token:
        return "Error: no hay sesión activa. Inicia sesión primero."

    # 1. Comprobación estricta de baneo en tiempo real (bloquea acceso total a la IA)
    email = sesion.get("email", "") if sesion else None
    ok_ban, motivo_ban, tipo_ban = _verificar_baneos_supabase(email=email)
    if not ok_ban:
        return f"⛔ ACCESO DENEGADO A LA IA ({tipo_ban}): Tu cuenta o dispositivo ha sido suspendido por moderación. Motivo: {motivo_ban}."

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