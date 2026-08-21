# KernossAI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![UI: CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)](https://github.com/TomSchimansky/CustomTkinter)
[![Website](https://img.shields.io/badge/Website-ldpcicnm2012.github.io%2FKernossAI-0284c7)](https://ldpcicnm2012.github.io/KernossAI/)

KernossAI es una aplicación de escritorio multiplataforma (Windows, macOS, Linux) orientada a la optimización de procesos de estudio y docencia. Integra herramientas de síntesis conceptual, generación y corrección de evaluaciones, análisis de calificaciones, síntesis de voz neuronal (TTS) y un canal de asistencia técnica con cifrado de extremo a extremo (E2EE).

---

## 📑 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Ejecución en Local](#-instalación-y-ejecución-en-local)
- [Configuración](#-configuración)
- [Compilación de Binarios](#-compilación-de-binarios)
- [Seguridad y Privacidad](#-seguridad-y-privacidad)
- [Licencia y Autoría](#-licencia-y-autoría)

---

## 🚀 Características Principales

1. **Mapas Mentales y Conceptuales**: Generación de diagramas jerárquicos multirama con distribución geométrica dinámica anticolisión, editor JSON en tiempo real y exportación en `.docx` y `.png`.
2. **Resumidor Académico**: Procesamiento de textos y documentos PDF con extracción de tesis clave, esquemas y conceptos fundamentales.
3. **Generador y Corrector de Evaluaciones**: Creación de pruebas tipo test y preguntas de desarrollo con autocorrección inmediata y desglose explicativo.
4. **Calculador de Calificaciones**: Registro de notas por asignatura con ponderaciones porcentuales y cálculo de medias ponderadas.
5. **Síntesis de Voz Neuronal (TTS)**: Conversión de texto a voz natural mediante modelos neuronales (`edge-tts` / `pygame`) para lectura de resúmenes y apuntes.
6. **Canal de Soporte con Cifrado E2EE**: Sistema de mensajería con cifrado simétrico/asimétrico derivado en cliente y sincronización en backend.
7. **Gestor de Sesiones y Multicuentas**: Soporte para múltiples perfiles locales y persistencia en Supabase (PostgreSQL).
8. **Modo Hogar y Acceso Controlado**: Sistema de validación de red local/remota y política de acceso por dispositivo.
9. **Internacionalización (i18n)**: Soporte multilenguaje integrado (Español, Inglés, Francés, Alemán) con recarga reactiva de interfaz.

---

## 🏗 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                   KernossAI Desktop UI                      │
│        (CustomTkinter + Matplotlib FigureCanvasTkAgg)       │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│      Lógica de Negocio       │ │      Servicios de Audio    │
│  - Generación de Mapas       │ │  - edge-tts Pipeline       │
│  - Evaluaciones y Ponderación│ │  - Pygame Audio Playback   │
│  - Exportación docx / png    │ │  - Normalizador de Voz     │
└──────────────┬───────────────┘ └────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Capa de Autenticación y Red                 │
│  - Cliente REST API (FastAPI Backend en Render)             │
│  - Base de Datos Supabase (PostgreSQL / RLS)                │
│  - Inferencia LLM: Groq (LLaMA 3.3 70B) & Google Gemini Pro │
│  - Cifrado Criptográfico E2EE (Cryptography Fernet / RSA)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Estructura del Proyecto

```
KernossAI/
├── assets/                  # Recursos gráficos, capturas y estilos
│   └── app-preview.png
├── main/                    # Código fuente de la aplicación
│   ├── auth_backend.py      # Autenticación, backend API, Supabase y LLM fallbacks
│   ├── config_manager.py    # Gestión de configuración local y estado de red
│   ├── i18n.py              # Diccionario de internacionalización (ES, EN, DE, FR)
│   ├── main.py              # Interfaz gráfica (CustomTkinter) y módulos de usuario
│   ├── tts_engine.py        # Motor de síntesis de voz (edge-tts / pygame)
│   ├── logo.ico             # Icono de aplicación para Windows
│   └── logo.icns            # Icono de aplicación para macOS
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Exclusiones de Git estándar
├── .nojekyll                # Desactivación de Jekyll para GitHub Pages
├── index.html               # Landing page oficial
├── requirements.txt         # Dependencias del proyecto
├── robots.txt               # Directivas para motores de búsqueda
├── sitemap.xml              # Mapa del sitio web
└── README.md                # Documentación técnica
```

---

## 📋 Requisitos Previos

- **Python**: 3.10 o superior.
- **Sistema Operativo**: Windows 10/11, macOS 12+ o Linux (Ubuntu 20.04+, Debian, Fedora).
- **Herramientas de compilación** (opcional, solo para generar ejecutables): `pyinstaller`.

---

## ⚙️ Instalación y Ejecución en Local

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/LDPCICNM2012/KernossAI.git
   cd KernossAI
   ```

2. **Crear y activar un entorno virtual**:
   ```bash
   # En Windows
   python -m venv venv
   .\venv\Scripts\activate

   # En Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**:
   ```bash
   python main/main.py
   ```

---

## 🔧 Configuración

El proyecto cuenta con valores por defecto para conectarse al backend oficial. Si deseas utilizar endpoints personalizados o claves de API propias para desarrollo offline:

1. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env` con tus credenciales de Supabase, Groq o Google Gemini.

---

## 📦 Compilación de Binarios

Para generar un ejecutable independiente (.exe en Windows):

```bash
pip install pyinstaller

pyinstaller --noconfirm --onedir --windowed \
  --name "KernossAI" \
  --icon "main/logo.ico" \
  --add-data "main/logo.ico;main" \
  main/main.py
```

---

## 🔒 Seguridad y Privacidad

- **Almacenamiento Local**: Los apuntes, documentos Word generados y esquemas se guardan en el disco duro del usuario.
- **Cifrado E2EE**: Los mensajes de soporte técnico se cifran antes de ser transmitidos al servidor.
- **Identificación de Hardware (HWID)**: La vinculación de sesiones utiliza un hash derivado de los componentes del equipo local para prevenir accesos no autorizados.

---

## 👤 Licencia y Autoría

Desarrollado y mantenido por **ldpcicnm2012 / Lander De Pablos** ([@LDPCICNM2012](https://github.com/LDPCICNM2012)).

Distribuido bajo la Licencia [MIT](LICENSE).
