import os
import sys
import re
import time
import uuid
import tempfile
import asyncio
import threading
import edge_tts
from KernossAI.core.config import obtener_ajustes_tts, guardar_ajustes_tts

VOICES_DISPONIBLES = {
    "es-ES-AlvaroNeural": "👨 Álvaro (España - Masculino)",
    "es-ES-ElviraNeural": "👩 Elvira (España - Femenino)",
    "es-MX-JorgeNeural":  "👨 Jorge (México - Masculino)",
    "es-MX-DaliaNeural":  "👩 Dalia (México - Femenino)",
    "es-AR-TomasNeural":  "👨 Tomás (Argentina - Masculino)",
    "es-AR-ElenaNeural":  "👩 Elena (Argentina - Femenino)",
    "en-US-GuyNeural":    "👨 Guy (Inglés - Masculino)",
    "en-US-JennyNeural":  "👩 Jenny (Inglés - Femenino)"
}

VELOCIDADES_DISPONIBLES = {
    "-20%": "Lenta (-20%)",
    "+0%":  "Normal (Predeterminada)",
    "+20%": "Rápida (+20%)",
    "+35%": "Muy Rápida (+35%)"
}

def limpiar_texto_para_tts(texto: str) -> str:
    """Elimina markdown, roles de chat, código JSON y caracteres extraños para lectura natural."""
    if not texto:
        return ""
    
    t = texto
    # 1. Quitar encabezados de rol del chat (ej: "🤖 KernossIA (GROQ):", "👤 Tú:")
    t = re.sub(r"[🤖👤]\s*[A-Za-z0-9_().\s-]+:\s*", " ", t)
    
    # 2. Quitar bloques de código completos
    t = re.sub(r"```[\s\S]*?```", " ", t)
    t = re.sub(r"`[^`]*`", " ", t)
    
    # 3. Quitar tablas markdown (| col | col |)
    t = re.sub(r"\|[^\n]+\|", " ", t)
    
    # 4. Quitar enlaces [texto](url) -> texto
    t = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", t)
    
    # 5. Quitar caracteres markdown (#, *, _, ~, >, =)
    t = re.sub(r"[#*_~`>=\-]+", " ", t)
    
    # 6. Reemplazos fonéticos amigables
    t = t.replace("->", " produce ")
    t = t.replace("!=", " distinto de ")
    t = t.replace("==", " igual a ")
    t = t.replace("✓", " correcto ")
    t = t.replace("✗", " incorrecto ")
    
    # 7. Normalizar espacios y saltos de línea
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _obtener_ruta_corta(ruta: str) -> str:
    """Obtiene la ruta corta 8.3 de Windows para evitar problemas de espacios o unicode en MCI."""
    if sys.platform == "win32":
        try:
            import ctypes
            buffer = ctypes.create_unicode_buffer(512)
            res = ctypes.windll.kernel32.GetShortPathNameW(ruta, buffer, 512)
            if res > 0 and buffer.value:
                return buffer.value
        except Exception:
            pass
        return ruta.replace("\\", "/")
    return ruta

class TTSEngine:
    def __init__(self):
        self._reproduciendo = False
        self._hilo_actual = None
        self._proceso_audio = None
        self._alias_mci_actual = None
        self._archivo_temp_actual = None
        self._lock = threading.Lock()

    def esta_reproduciendo(self) -> bool:
        return self._reproduciendo

    def detener(self):
        """Detiene de forma inmediata cualquier audio y libera recursos del sistema."""
        with self._lock:
            self._reproduciendo = False

            if sys.platform == "win32":
                try:
                    import ctypes
                    mci = ctypes.windll.winmm.mciSendStringW
                    if self._alias_mci_actual:
                        mci(f"stop {self._alias_mci_actual}", None, 0, None)
                        mci(f"close {self._alias_mci_actual}", None, 0, None)
                    mci("close all", None, 0, None)
                except Exception:
                    pass
            else:
                if self._proceso_audio:
                    try:
                        self._proceso_audio.terminate()
                        self._proceso_audio = None
                    except Exception:
                        pass

            # Limpiar archivo temporal si existe
            if self._archivo_temp_actual:
                try:
                    if os.path.exists(self._archivo_temp_actual):
                        os.remove(self._archivo_temp_actual)
                except Exception:
                    pass
                self._archivo_temp_actual = None

    def hablar(self, texto: str, callback_estado=None):
        """
        Sintetiza y reproduce el texto en voz alta en un hilo demonio.
        Utiliza un archivo temporal único por cada petición para evitar bloqueos en Windows.
        """
        self.detener()
        texto_limpio = limpiar_texto_para_tts(texto)
        if not texto_limpio:
            if callback_estado:
                callback_estado(False)
            return

        self._reproduciendo = True
        if callback_estado:
            callback_estado(True)

        self._hilo_actual = threading.Thread(
            target=self._worker_reproducir,
            args=(texto_limpio, callback_estado),
            daemon=True
        )
        self._hilo_actual.start()

    def _worker_reproducir(self, texto: str, callback_estado):
        temp_file = None
        alias_mci = f"kns_{uuid.uuid4().hex[:8]}"

        try:
            voz, velocidad = obtener_ajustes_tts()
            if voz not in VOICES_DISPONIBLES:
                voz = "es-ES-AlvaroNeural"
            if velocidad not in VELOCIDADES_DISPONIBLES:
                velocidad = "+0%"

            # Generar archivo temporal con nombre único
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"{alias_mci}.mp3")
            
            with self._lock:
                self._archivo_temp_actual = temp_file
                self._alias_mci_actual = alias_mci

            # 1. Generar audio con edge-tts (soporta textos largos)
            async def _generar():
                communicate = edge_tts.Communicate(texto, voz, rate=velocidad)
                await communicate.save(temp_file)

            asyncio.run(_generar())

            if not self._reproduciendo or not os.path.exists(temp_file):
                if callback_estado:
                    callback_estado(False)
                return

            # 2. Reproducción multiplataforma nativa
            if sys.platform == "win32":
                self._reproducir_windows(temp_file, alias_mci)
            elif sys.platform == "darwin": # macOS
                self._reproducir_macos(temp_file)
            else: # Linux
                self._reproducir_linux(temp_file)

        except Exception as e:
            print(f"[TTS Error] {e}")
        finally:
            self._reproduciendo = False
            
            # Limpiar archivo temporal al terminar
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

            if callback_estado:
                callback_estado(False)

    def _reproducir_windows(self, temp_file: str, alias_mci: str):
        """Reproduce MP3 en Windows con MCI y ruta 8.3 inmune a bloqueos."""
        import ctypes
        mci = ctypes.windll.winmm.mciSendStringW

        short_path = _obtener_ruta_corta(temp_file)
        
        # Abrir con alias único
        mci(f"close {alias_mci}", None, 0, None)
        cmd_open = f'open "{short_path}" type mpegvideo alias {alias_mci}'
        res_open = mci(cmd_open, None, 0, None)

        if res_open != 0:
            # Fallback en caso de que MCI tenga algún conflicto con la tarjeta de sonido
            self._reproducir_windows_fallback(short_path)
            return

        mci(f"play {alias_mci}", None, 0, None)

        buf = ctypes.create_unicode_buffer(128)
        while self._reproduciendo:
            mci(f"status {alias_mci} mode", buf, 128, None)
            if buf.value != "playing":
                break
            time.sleep(0.15)

        mci(f"stop {alias_mci}", None, 0, None)
        mci(f"close {alias_mci}", None, 0, None)

    def _reproducir_windows_fallback(self, file_path: str):
        """Fallback con MediaPlayer COM en segundo plano si MCI falla."""
        try:
            ps_cmd = (
                f"$p = New-Object -ComObject WMPlayer.OCX; "
                f"$p.URL = '{file_path}'; "
                f"$p.controls.play(); "
                f"while($p.playState -ne 1 -and $p.playState -ne 8) {{ Start-Sleep -Milliseconds 150 }}"
            )
            self._proceso_audio = subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                creationflags=0x08000000 # CREATE_NO_WINDOW
            )
            while self._reproduciendo and self._proceso_audio.poll() is None:
                time.sleep(0.15)
            if self._proceso_audio and self._proceso_audio.poll() is None:
                self._proceso_audio.terminate()
        except Exception:
            pass

    def _reproducir_macos(self, temp_file: str):
        """Reproduce en macOS con 'afplay' integrado en el sistema."""
        try:
            self._proceso_audio = subprocess.Popen(["afplay", temp_file])
            while self._reproduciendo and self._proceso_audio.poll() is None:
                time.sleep(0.15)
            if self._proceso_audio and self._proceso_audio.poll() is None:
                self._proceso_audio.terminate()
        except Exception:
            pass

    def _reproducir_linux(self, temp_file: str):
        """Reproduce en Linux con los reproductores de audio estándar disponibles en el sistema."""
        reproductores = [
            ("mpv", ["mpv", "--no-video", "--really-quiet", temp_file]),
            ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file]),
            ("mpg123", ["mpg123", "-q", temp_file]),
            ("mpg321", ["mpg321", "-q", temp_file]),
            ("paplay", ["paplay", temp_file]),
            ("play", ["play", "-q", temp_file]),
            ("cvlc", ["cvlc", "--play-and-exit", temp_file])
        ]
        
        cmd_a_ejecutar = None
        for nombre, cmd in reproductores:
            if subprocess.call(["which", nombre], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                cmd_a_ejecutar = cmd
                break

        if cmd_a_ejecutar:
            try:
                self._proceso_audio = subprocess.Popen(cmd_a_ejecutar)
                while self._reproduciendo and self._proceso_audio.poll() is None:
                    time.sleep(0.15)
                if self._proceso_audio and self._proceso_audio.poll() is None:
                    self._proceso_audio.terminate()
            except Exception:
                pass

# Instancia global reutilizable
tts_engine = TTSEngine()
