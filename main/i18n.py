"""
KernossIA — Sistema de Internacionalización (i18n)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Soporte completo multi-idioma (Español, English, Deutsch, Français)
100% compatible con Windows, macOS y Linux.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any

IDIOMAS_DISPONIBLES = {
    "es": "🇪🇸 Español",
    "en": "🇬🇧 English",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français"
}

# Diccionario maestro de traducciones
TRADUCCIONES: Dict[str, Dict[str, str]] = {
    "es": {
        # General & App
        "app_nombre": "⚡ KernossIA",
        "app_subtitulo": "Suite de Estudio & Educación con Inteligencia Artificial",
        "app_tagline": "Suite de Estudio 2026",
        "btn_novedades": "✨ Novedades v1.6",
        "btn_ajustes": "⚙️ Ajustes / Configuración",
        "btn_cerrar_sesion": "🚪 Cerrar Sesión",
        "lbl_rol_alumno": "Alumno",
        "lbl_rol_profesor": "Profesor",
        "lbl_selecciona_idioma": "🌐 Idioma / Language:",
        
        # Login & Registro
        "tab_login": "Iniciar Sesión",
        "tab_registro": "Registrarse",
        "lbl_email": "Correo electrónico",
        "placeholder_email": "tu@correo.com",
        "lbl_pass": "Contraseña",
        "placeholder_pass": "••••••••",
        "placeholder_pass_reg": "Mínimo 6 caracteres",
        "lbl_nombre": "Nombre completo",
        "placeholder_nombre": "Tu nombre",
        "lbl_rol": "Rol",
        "btn_login": "Iniciar Sesión",
        "btn_registro": "Crear Cuenta",
        "login_conectando": "Conectando con el servidor...",
        "reg_creando": "Creando cuenta en el servidor...",
        "login_error_campos": "Completa todos los campos.",
        "login_error_correo": "Correo inválido.",
        "login_error_pass_len": "La contraseña debe tener al menos 6 caracteres.",
        "login_privacidad": "🔒 100% Gratuito y Privado • Tus apuntes se guardan en tu equipo.",
        
        # Sidebar & Navigation
        "btn_home": "🏠  Inicio / Chat IA",
        "hdr_historial": "🕒 HISTORIAL DE CHAT",
        "btn_nuevo_chat": "➕ Nuevo",
        "hdr_modulos_estudio": "MÓDULOS DE ESTUDIO",
        "hdr_herramientas_docente": "HERRAMIENTAS DOCENTE",
        
        # Módulos Sidebar
        "mod_mapas": "🧠 Mapas Mentales",
        "mod_calculador": "📊 Calculador de Medias",
        "mod_apuntador": "📝 Apuntador de Notas",
        "mod_resumidor": "🔍 Resumidor de Textos AI",
        "mod_examenes": "🎯 Generador de Exámenes",
        "mod_ayudante": "🤖 Ayudante de Problemas",
        "mod_agenda": "📅 Agenda de Estudios",
        "mod_ejercicios": "✏️ Creador de Ejercicios",
        "mod_corrector": "📋 Corrector de Exámenes",
        "mod_soporte": "🛡️ Soporte Oficial & Mensajes E2EE",
        "btn_admin_panel": "👑 Panel de Moderación & Bans",
        
        # Home & Chat
        "home_bienvenida": "¡Bienvenido, {rol} {nombre}!",
        "home_estado_ia": "🟢 Asistente IA Activo (Groq & Gemini) • ¿Qué necesitas estudiar o preparar hoy?",
        "home_placeholder_input": "Escribe tu pregunta, tema de examen o consulta para resolverla con IA...",
        "btn_consultar_ia": "⚡ Consultar IA",
        "btn_escuchar": "🔊 Escuchar",
        "btn_word": "📄 Word",
        "opt_groq": "⚡ Groq (Rápido)",
        "opt_gemini": "🧠 Gemini (Profundo)",
        "btn_detener_audio": "⏹ Detener",
        
        # Ajustes
        "ajustes_titulo": "⚙️ Ajustes & Configuración de KernossIA",
        "ajustes_subtitulo": "Personaliza el idioma, lector de voz (TTS) y preferencias",
        "ajustes_sec_idioma": "🌐 Idioma de la Aplicación",
        "ajustes_lbl_idioma": "Selecciona el idioma de la interfaz:",
        "ajustes_sec_rol": "🎓 Modalidad y Rol de Cuenta",
        "ajustes_lbl_rol": "Modalidad de trabajo activa:",
        "ajustes_sec_multi": "👥 Gestor de Multicuentas",
        "ajustes_btn_agregar_cuenta": "➕ Iniciar Sesión en Otra Cuenta",
        "ajustes_sec_voz": "🔊 Lector en Voz Alta con IA (TTS)",
        "ajustes_lbl_voz": "Voz de Lectura:",
        "ajustes_lbl_velocidad": "Velocidad:",
        "ajustes_btn_probar": "🔊 Probar Voz",
        "ajustes_sec_privacidad": "⚠️ Zona de Privacidad — Cuenta",
        "ajustes_btn_borrar_cuenta": "🗑️ Borrar Mi Cuenta Definitivamente",
        "ajustes_btn_guardar": "💾 Guardar Ajustes",
        "ajustes_btn_cancelar": "Cancelar",
        "ajustes_guardado_ok": "Ajustes guardados correctamente.",
        "ajustes_aviso_reinicio": "El idioma se ha actualizado correctamente.",

        # Hogar Principal Modal
        "hogar_titulo": "🏠 ¿Estás en tu Hogar Principal?",
        "hogar_subtitulo": "Control de ubicación y protección de cuenta compartida",
        "hogar_btn_temporal": "✈️ Estudiar Fuera de Casa (De viaje)",
        "hogar_btn_actualizar": "🏡 Establecer Esta Red como mi Hogar Principal",

        # Novedades v1.6
        "modal_novedades_titulo": "🎉 ¡Bienvenido a KernossIA v{version}!",
        "modal_novedades_subtitulo": "Descubre las nuevas funciones y mejoras añadidas en esta versión:",
        "modal_novedades_btn_empezar": "🚀 ¡Empezar a Usar KernossIA!",
        "nov_item_soporte_tit": "🛡️ Soporte Técnico Oficial E2EE con Categorización",
        "nov_item_soporte_desc": "Canal de chat cifrado de extremo a extremo (E2EE) con selector de motivo (dudas, IA, bugs, cuentas) y respuestas en tiempo real.",
        "nov_item_multi_tit": "👥 Gestor de Multicuentas en Ajustes",
        "nov_item_multi_desc": "Inicia sesión con múltiples cuentas en el mismo equipo y alterna entre ellas con 1 solo clic (🔄 Cambiar) sin volver a escribir contraseñas.",
        "nov_item_rol_tit": "🎓 Selector de Rol Académico (Alumno / Profesor)",
        "nov_item_rol_desc": "Cambia tu modalidad en cualquier momento desde Ajustes para desbloquear el Creador de Ejercicios y Corrector Automático sin reiniciar.",
        "nov_item_mod_tit": "⛔ Vigilante de Moderación en Vivo & Pantalla de Bloqueo",
        "nov_item_mod_desc": "Detección instantánea de sanciones en tiempo real con cierre automático de sesión, revocación total de acceso a la IA y pantalla roja informativa.",
        "nov_item_cloud_tit": "⚡ Persistencia de Sesión & Cloud Storage Supabase",
        "nov_item_cloud_desc": "Conexión segura con la nube de Supabase para evitar deslogueos al cerrar la aplicación y almacenar datos de forma perpetua.",
        "nov_item_hwid_tit": "💻 Blindaje Anti-Fraude de Hardware (HWID)",
        "nov_item_hwid_desc": "Identificación criptográfica de dispositivos para garantizar la seguridad de cuentas y prevenir el abuso de accesos.",

        # Actualización OTA
        "ota_btn_actualizar": "⚡ Actualizar Automáticamente (OTA)",
        "ota_btn_web": "🌐 Descargar en Web",
        "ota_descargando": "Descargando actualización...",
        "ota_instalando": "⚡ Instalando actualización y reiniciando...",
        "ota_error": "Error al descargar actualización: {err}",

        # Vinculación & Tutoría Alumno <-> Profesor
        "btn_tutoria_alumno": "👨‍🏫 Mi Profesor",
        "btn_tutoria_profesor": "🎓 Mis Alumnos",
        "tutoria_modal_titulo_alumno": "👨‍🏫 Mi Profesor Tutor & Consultas",
        "tutoria_modal_titulo_profesor": "🎓 Panel de Tutoría: Alumnos & Solicitudes",
        "tutoria_tab_profesores": "👨‍🏫 Profesores Disponibles",
        "tutoria_tab_mi_profe": "💬 Chat con mi Profesor",
        "tutoria_tab_solicitudes": "🔔 Solicitudes Pendientes",
        "tutoria_tab_alumnos": "👥 Mis Alumnos Vinculados",
        "tutoria_btn_solicitar": "📨 Solicitar Vinculación",
        "tutoria_btn_aceptar": "✅ Aceptar Alumno",
        "tutoria_btn_rechazar": "❌ Rechazar",
        "tutoria_btn_desvincular": "⚠️ Desvincular",
        "tutoria_sin_profes": "No hay profesores registrados en este momento.",
        "tutoria_solicitud_pendiente": "⏳ Solicitud pendiente de confirmación con el profesor {nombre} ({email})",

        # Soporte E2EE
        "sop_titulo_ventana": "🛡️ Soporte Oficial KernossAI — Chat Cifrado E2EE",
        "sop_subtitulo": "🔒 Cifrado de Extremo a Extremo (E2EE) Activo • Cero Conocimiento en Servidor",
        "sop_aviso_beta": "🧪 Función beta • Cualquier error, comuníquelo en GitHub",
        "sop_lbl_motivo": "📌 Motivo:",
        "sop_plh_input": "Escribe tu mensaje a soporte (se cifrará antes de enviarse)...",
        "sop_btn_enviar": "Enviar 📤",

        # Módulo: Calculador de Medias
        "calc_titulo": "📊 Calculadora de Medias Ponderadas",
        "calc_subtitulo": "Organiza, pondera y visualiza el progreso de tus calificaciones",
        "calc_lbl_materia": "Materia o Asignatura",
        "calc_plh_materia": "Ej: Matemáticas, Física...",
        "calc_lbl_nota": "Nota Directa (0-10)",
        "calc_plh_nota": "Ej: 9.5",
        "calc_lbl_pct": "% del Total (Ponderación)",
        "calc_plh_pct": "Ej: 40",
        "calc_btn_guardar_nota": "➕ Guardar Nota Directa",
        "calc_btn_bloques": "📂 Agregar Bloques / Subnotas",
        "calc_hdr_registro": "Registro Detallado",
        "calc_hdr_grafica": "Gráfica de Rendimiento",
        "calc_btn_calcular": "⚡ Calcular Media Final",
        "calc_btn_limpiar": "🗑️ Limpiar Todo",
        "calc_btn_exportar": "📄 Exportar Informe",

        # Módulo: Apuntador de Notas
        "apunt_titulo": "📝 Apuntador de Notas & Exportación Word",
        "apunt_subtitulo": "Tus notas académicas privadas y redactadas con asistencia IA",
        "apunt_btn_nueva": "➕ Nueva Nota",
        "apunt_btn_leer": "🔊 Leer",
        "apunt_btn_guardar": "💾 Guardar",
        "apunt_btn_word": "📄 Word",
        "apunt_btn_borrar": "🗑️ Borrar",
        "apunt_lbl_sin_nota": "Seleccione una nota",

        # Módulo: Resumidor de Textos
        "resum_titulo": "🔍 Resumidor de Textos con IA",
        "resum_subtitulo": "Genera síntesis rigurosas y esquemáticas de cualquier temario",
        "resum_lbl_entrada": "Pega tus apuntes o tema aquí:",
        "resum_lbl_salida": "Resumen Riguroso Generado por IA:",
        "resum_btn_resumir": "⚡ Generar Resumen con IA",
        "resum_btn_limpiar": "🗑️ Limpiar",
        "resum_btn_copiar": "📋 Copiar",

        # Módulo: Generador de Exámenes
        "exam_titulo": "🎯 Generador de Exámenes Tipo Test & Desarrollo",
        "exam_subtitulo": "Crea pruebas de evaluación a partir de tus temas de estudio",
        "exam_lbl_tema": "Tema o Contenido del Examen:",
        "exam_lbl_tipo": "Tipo de Examen:",
        "exam_lbl_preguntas": "Número de Preguntas:",
        "exam_lbl_dificultad": "Dificultad:",
        "exam_btn_generar": "⚡ Generar Examen con IA",

        # Módulo: Ayudante de Problemas
        "ayud_titulo": "🤖 Ayudante y Resolutor de Problemas con IA",
        "ayud_subtitulo": "Explicaciones paso a paso de matemáticas, ciencias, sintaxis y programación",
        "ayud_lbl_enunciado": "Escribe el enunciado de tu problema o ejercicio:",
        "ayud_lbl_solucion": "Solución y Explicación Paso a Paso:",
        "ayud_btn_resolver": "⚡ Resolver Paso a Paso",

        # Módulo: Mapas Mentales
        "mapa_titulo": "🧠 Generador de Mapas Mentales con IA",
        "mapa_subtitulo": "Visualiza la jerarquía conceptual de cualquier tema académico",
        "mapa_lbl_tema": "Concepto Principal o Tema de Estudio:",
        "mapa_btn_generar": "⚡ Generar Mapa Mental",

        # Módulo: Agenda de Estudios
        "agenda_titulo": "📅 Planificador y Agenda de Estudio",
        "agenda_subtitulo": "Organiza tus entregas, exámenes y sesiones de repaso",
        "agenda_btn_anadir": "➕ Añadir Tarea / Examen",

        # Módulo Docente: Creador de Ejercicios
        "cread_titulo": "✏️ Creador de Ejercicios y Rúbricas Docentes",
        "cread_subtitulo": "Diseña actividades personalizadas con soluciones para tus alumnos",
        "cread_btn_generar": "⚡ Generar Ejercicios",

        # Módulo Docente: Corrector de Exámenes
        "corr_titulo": "📋 Corrector Automático y Evaluador Docente",
        "corr_subtitulo": "Analiza respuestas de alumnos y genera feedback pedagógico",
        "corr_btn_corregir": "⚡ Corregir y Evaluar"
    },

    "en": {
        # General & App
        "app_nombre": "⚡ KernossAI",
        "app_subtitulo": "AI-Powered Study & Education Suite",
        "app_tagline": "Study Suite 2026",
        "btn_novedades": "✨ What's New v1.6",
        "btn_ajustes": "⚙️ Settings / Config",
        "btn_cerrar_sesion": "🚪 Log Out",
        "lbl_rol_alumno": "Student",
        "lbl_rol_profesor": "Teacher",
        "lbl_selecciona_idioma": "🌐 Language / Idioma:",
        
        # Login & Register
        "tab_login": "Sign In",
        "tab_registro": "Register",
        "lbl_email": "Email address",
        "placeholder_email": "you@email.com",
        "lbl_pass": "Password",
        "placeholder_pass": "••••••••",
        "placeholder_pass_reg": "At least 6 characters",
        "lbl_nombre": "Full name",
        "placeholder_nombre": "Your name",
        "lbl_rol": "Role",
        "btn_login": "Sign In",
        "btn_registro": "Create Account",
        "login_conectando": "Connecting to server...",
        "reg_creando": "Creating account on server...",
        "login_error_campos": "Please fill in all fields.",
        "login_error_correo": "Invalid email address.",
        "login_error_pass_len": "Password must have at least 6 characters.",
        "login_privacidad": "🔒 100% Free & Private • Your notes stay on your computer.",
        
        # Sidebar & Navigation
        "btn_home": "🏠  Home / AI Chat",
        "hdr_historial": "🕒 CHAT HISTORY",
        "btn_nuevo_chat": "➕ New",
        "hdr_modulos_estudio": "STUDY MODULES",
        "hdr_herramientas_docente": "TEACHER TOOLS",
        
        # Modules Sidebar
        "mod_mapas": "🧠 Mind Maps",
        "mod_calculador": "📊 Grade Calculator",
        "mod_apuntador": "📝 Class Notes & Word",
        "mod_resumidor": "🔍 AI Text Summarizer",
        "mod_examenes": "🎯 Exam Generator",
        "mod_ayudante": "🤖 Problem Solver",
        "mod_agenda": "📅 Study Planner",
        "mod_ejercicios": "✏️ Exercise Creator",
        "mod_corrector": "📋 Exam Grader",
        "mod_soporte": "🛡️ Official Support & E2EE Messages",
        "btn_admin_panel": "👑 Moderation & Bans Panel",
        
        # Home & Chat
        "home_bienvenida": "Welcome, {rol} {nombre}!",
        "home_estado_ia": "🟢 AI Assistant Active (Groq & Gemini) • What would you like to study today?",
        "home_placeholder_input": "Type your question, study topic, or prompt to solve with AI...",
        "btn_consultar_ia": "⚡ Ask AI",
        "btn_escuchar": "🔊 Listen",
        "btn_word": "📄 Word",
        "opt_groq": "⚡ Groq (Fast)",
        "opt_gemini": "🧠 Gemini (Deep)",
        "btn_detener_audio": "⏹ Stop",
        
        # Settings
        "ajustes_titulo": "⚙️ Settings & Configuration",
        "ajustes_subtitulo": "Customize language, AI voice reader (TTS) and preferences",
        "ajustes_sec_idioma": "🌐 Application Language",
        "ajustes_lbl_idioma": "Select interface language:",
        "ajustes_sec_rol": "🎓 Account Role & Mode",
        "ajustes_lbl_rol": "Active working mode:",
        "ajustes_sec_multi": "👥 Multi-Account Switcher",
        "ajustes_btn_agregar_cuenta": "➕ Sign in to Another Account",
        "ajustes_sec_voz": "🔊 AI Voice Reader (TTS)",
        "ajustes_lbl_voz": "Reading Voice:",
        "ajustes_lbl_velocidad": "Speed:",
        "ajustes_btn_probar": "🔊 Test Voice",
        "ajustes_sec_privacidad": "⚠️ Privacy Zone — Account",
        "ajustes_btn_borrar_cuenta": "🗑️ Permanently Delete My Account",
        "ajustes_btn_guardar": "💾 Save Settings",
        "ajustes_btn_cancelar": "Cancel",
        "ajustes_guardado_ok": "Settings saved successfully.",
        "ajustes_aviso_reinicio": "Language updated successfully.",
        
        # Household Confirmation Modal
        "hogar_titulo": "🏠 Are you at your Primary Study Home?",
        "hogar_subtitulo": "Location control and shared account protection",
        "hogar_btn_temporal": "✈️ Study Away From Home (Traveling)",
        "hogar_btn_actualizar": "🏡 Set This Network as my Primary Home",

        # What's New v1.6
        "modal_novedades_titulo": "🎉 Welcome to KernossAI v{version}!",
        "modal_novedades_subtitulo": "Discover the new features and improvements added in this version:",
        "modal_novedades_btn_empezar": "🚀 Start Using KernossAI!",
        "nov_item_soporte_tit": "🛡️ Official E2EE Technical Support with Categories",
        "nov_item_soporte_desc": "End-to-end encrypted direct chat channel with kernossai@support.com with topic selector (questions, AI, bugs, accounts) and real-time replies.",
        "nov_item_multi_tit": "👥 Multi-Account Switcher in Settings",
        "nov_item_multi_desc": "Log in with multiple accounts on the same computer and switch between them in 1 click (🔄 Switch) without retyping passwords.",
        "nov_item_rol_tit": "🎓 Academic Role Selector (Student / Teacher)",
        "nov_item_rol_desc": "Change your mode anytime from Settings to unlock the Exercise Creator and Exam Grader without restarting.",
        "nov_item_mod_tit": "⛔ Live Moderation Sentinel & Lockout Screen",
        "nov_item_mod_desc": "Instant real-time sanction detection with automatic logout, total AI access revocation, and informational red screen.",
        "nov_item_cloud_tit": "⚡ Session Persistence & Supabase Cloud Storage",
        "nov_item_cloud_desc": "Secure connection to Supabase cloud preventing unintentional logouts upon app restart and keeping data permanently stored.",
        "nov_item_hwid_tit": "💻 Hardware Anti-Fraud Shield (HWID)",
        "nov_item_hwid_desc": "Cryptographic hardware device fingerprinting to protect accounts and prevent unauthorized abuse.",

        # OTA Update
        "ota_btn_actualizar": "⚡ Auto-Update Now (OTA)",
        "ota_btn_web": "🌐 Download from Web",
        "ota_descargando": "Downloading update...",
        "ota_instalando": "⚡ Installing update and restarting...",
        "ota_error": "Error downloading update: {err}",

        # Tutoring & Linking Student <-> Teacher
        "btn_tutoria_alumno": "👨‍🏫 My Teacher",
        "btn_tutoria_profesor": "🎓 My Students",
        "tutoria_modal_titulo_alumno": "👨‍🏫 My Tutor Teacher & Questions",
        "tutoria_modal_titulo_profesor": "🎓 Tutoring Panel: Students & Requests",
        "tutoria_tab_profesores": "👨‍🏫 Available Teachers",
        "tutoria_tab_mi_profe": "💬 Chat with my Teacher",
        "tutoria_tab_solicitudes": "🔔 Pending Requests",
        "tutoria_tab_alumnos": "👥 My Connected Students",
        "tutoria_btn_solicitar": "📨 Request Connection",
        "tutoria_btn_aceptar": "✅ Accept Student",
        "tutoria_btn_rechazar": "❌ Reject",
        "tutoria_btn_desvincular": "⚠️ Disconnect",
        "tutoria_sin_profes": "No teachers registered at this time.",
        "tutoria_solicitud_pendiente": "⏳ Connection request pending with teacher {nombre} ({email})",

        # Support E2EE
        "sop_titulo_ventana": "🛡️ Official Support KernossAI — E2EE Encrypted Chat",
        "sop_subtitulo": "🔒 End-to-End Encryption (E2EE) Active • Zero Knowledge on Server",
        "sop_aviso_beta": "🧪 Beta feature • Report any issues on GitHub",
        "sop_lbl_motivo": "📌 Reason / Topic:",
        "sop_plh_input": "Type your message to support (encrypted before sending)...",
        "sop_btn_enviar": "Send 📤",

        # Module: Grade Calculator
        "calc_titulo": "📊 Weighted Grade Calculator",
        "calc_subtitulo": "Organize, weight and track your academic grades progress",
        "calc_lbl_materia": "Subject or Course",
        "calc_plh_materia": "e.g.: Mathematics, Physics...",
        "calc_lbl_nota": "Direct Grade (0-10)",
        "calc_plh_nota": "e.g.: 9.5",
        "calc_lbl_pct": "% of Total (Weighting)",
        "calc_plh_pct": "e.g.: 40",
        "calc_btn_guardar_nota": "➕ Save Direct Grade",
        "calc_btn_bloques": "📂 Add Sub-grades / Blocks",
        "calc_hdr_registro": "Detailed Grade Log",
        "calc_hdr_grafica": "Performance Chart",
        "calc_btn_calcular": "⚡ Calculate Final Average",
        "calc_btn_limpiar": "🗑️ Clear All",
        "calc_btn_exportar": "📄 Export Report",

        # Module: Class Notes
        "apunt_titulo": "📝 Class Notes & Word Export",
        "apunt_subtitulo": "Your private class notes drafted with AI assistance",
        "apunt_btn_nueva": "➕ New Note",
        "apunt_btn_leer": "🔊 Listen",
        "apunt_btn_guardar": "💾 Save",
        "apunt_btn_word": "📄 Word",
        "apunt_btn_borrar": "🗑️ Delete",
        "apunt_lbl_sin_nota": "Select a note",

        # Module: AI Summarizer
        "resum_titulo": "🔍 AI Text Summarizer",
        "resum_subtitulo": "Generate rigorous and structured summaries of any syllabus",
        "resum_lbl_entrada": "Paste your notes or text here:",
        "resum_lbl_salida": "AI-Generated Rigorous Summary:",
        "resum_btn_resumir": "⚡ Generate Summary with AI",
        "resum_btn_limpiar": "🗑️ Clear",
        "resum_btn_copiar": "📋 Copy",

        # Module: Exam Generator
        "exam_titulo": "🎯 Exam & Quiz Generator",
        "exam_subtitulo": "Create evaluation exams and quizzes from your study topics",
        "exam_lbl_tema": "Exam Topic or Content:",
        "exam_lbl_tipo": "Exam Format:",
        "exam_lbl_preguntas": "Number of Questions:",
        "exam_lbl_dificultad": "Difficulty:",
        "exam_btn_generar": "⚡ Generate Exam with AI",

        # Module: Problem Solver
        "ayud_titulo": "🤖 AI Problem Solver & Academic Assistant",
        "ayud_subtitulo": "Step-by-step solutions for math, science, syntax, and coding",
        "ayud_lbl_enunciado": "Enter your problem or exercise prompt:",
        "ayud_lbl_solucion": "Solution & Step-by-Step Explanation:",
        "ayud_btn_resolver": "⚡ Solve Step by Step",

        # Module: Mind Maps
        "mapa_titulo": "🧠 AI Mind Map Generator",
        "mapa_subtitulo": "Visualize the conceptual hierarchy of any academic topic",
        "mapa_lbl_tema": "Main Concept or Study Topic:",
        "mapa_btn_generar": "⚡ Generate Mind Map",

        # Module: Study Planner
        "agenda_titulo": "📅 Study Planner & Calendar",
        "agenda_subtitulo": "Organize your deadlines, exams and revision sessions",
        "agenda_btn_anadir": "➕ Add Task / Exam",

        # Teacher Module: Exercise Creator
        "cread_titulo": "✏️ Exercise & Rubric Creator for Teachers",
        "cread_subtitulo": "Design custom activities with answer keys for your students",
        "cread_btn_generar": "⚡ Generate Exercises",

        # Teacher Module: Exam Grader
        "corr_titulo": "📋 Automated Exam Grader & Assessment Assistant",
        "corr_subtitulo": "Analyze student answers and generate pedagogical feedback",
        "corr_btn_corregir": "⚡ Grade and Evaluate"
    },

    "de": {
        # General & App
        "app_nombre": "⚡ KernossAI",
        "app_subtitulo": "KI-gestützte Studien- & Bildungssuite",
        "app_tagline": "Studien-Suite 2026",
        "btn_novedades": "✨ Neuigkeiten v1.6",
        "btn_ajustes": "⚙️ Einstellungen",
        "btn_cerrar_sesion": "🚪 Abmelden",
        "lbl_rol_alumno": "Schüler / Student",
        "lbl_rol_profesor": "Lehrer / Dozent",
        "lbl_selecciona_idioma": "🌐 Sprache / Language:",
        
        # Login & Register
        "tab_login": "Anmelden",
        "tab_registro": "Registrieren",
        "lbl_email": "E-Mail-Adresse",
        "placeholder_email": "deine@email.de",
        "lbl_pass": "Passwort",
        "placeholder_pass": "••••••••",
        "placeholder_pass_reg": "Mindestens 6 Zeichen",
        "lbl_nombre": "Vollständiger Name",
        "placeholder_nombre": "Dein Name",
        "lbl_rol": "Rolle",
        "btn_login": "Anmelden",
        "btn_registro": "Konto Erstellen",
        "login_conectando": "Verbindung zum Server wird hergestellt...",
        "reg_creando": "Konto wird auf dem Server erstellt...",
        "login_error_campos": "Bitte füllen Sie alle Felder aus.",
        "login_error_correo": "Ungültige E-Mail-Adresse.",
        "login_error_pass_len": "Das Passwort muss mindestens 6 Zeichen lang sein.",
        "login_privacidad": "🔒 100% Kostenlos & Privat • Ihre Notizen bleiben auf Ihrem Computer.",
        
        # Sidebar & Navigation
        "btn_home": "🏠  Startseite / KI-Chat",
        "hdr_historial": "🕒 CHAT-VERLAUF",
        "btn_nuevo_chat": "➕ Neu",
        "hdr_modulos_estudio": "STUDIENMODULE",
        "hdr_herramientas_docente": "LEHRERWERKZEUGE",
        
        # Modules Sidebar
        "mod_mapas": "🧠 Mindmaps",
        "mod_calculador": "📊 Notenrechner",
        "mod_apuntador": "📝 Notizen & Word",
        "mod_resumidor": "🔍 KI-Text-Zusammenfasser",
        "mod_examenes": "🎯 Prüfungsgenerator",
        "mod_ayudante": "🤖 Problem-Löser",
        "mod_agenda": "📅 Studienplaner",
        "mod_ejercicios": "✏️ Übungsersteller",
        "mod_corrector": "📋 Prüfungskorrektor",
        "mod_soporte": "🛡️ Offizieller Support & E2EE",
        "btn_admin_panel": "👑 Moderations- & Sperrpanel",
        
        # Home & Chat
        "home_bienvenida": "Willkommen, {rol} {nombre}!",
        "home_estado_ia": "🟢 KI-Assistent Aktiv (Groq & Gemini) • Was möchtest du heute lernen?",
        "home_placeholder_input": "Frage eingeben, Thema oder Prüfungsaufgabe für die KI...",
        "btn_consultar_ia": "⚡ KI Fragen",
        "btn_escuchar": "🔊 Vorlesen",
        "btn_word": "📄 Word",
        "opt_groq": "⚡ Groq (Schnell)",
        "opt_gemini": "🧠 Gemini (Gründlich)",
        "btn_detener_audio": "⏹ Stopp",
        
        # Settings
        "ajustes_titulo": "⚙️ Einstellungen & Konfiguration",
        "ajustes_subtitulo": "Sprache, KI-Sprachausgabe (TTS) und Präferenzen anpassen",
        "ajustes_sec_idioma": "🌐 Anwendungssprache",
        "ajustes_lbl_idioma": "Oberflächensprache auswählen:",
        "ajustes_sec_rol": "🎓 Kontomodus & Rolle",
        "ajustes_lbl_rol": "Aktiver Arbeitsmodus:",
        "ajustes_sec_multi": "👥 Multi-Account-Manager",
        "ajustes_btn_agregar_cuenta": "➕ Weiteres Konto Hinzufügen",
        "ajustes_sec_voz": "🔊 KI-Sprachausgabe (TTS)",
        "ajustes_lbl_voz": "Vorlesestimme:",
        "ajustes_lbl_velocidad": "Geschwindigkeit:",
        "ajustes_btn_probar": "🔊 Stimme Testen",
        "ajustes_sec_privacidad": "⚠️ Datenschutzbereich — Konto",
        "ajustes_btn_borrar_cuenta": "🗑️ Mein Konto Dauerhaft Löschen",
        "ajustes_btn_guardar": "💾 Einstellungen Speichern",
        "ajustes_btn_cancelar": "Abbrechen",
        "ajustes_guardado_ok": "Einstellungen erfolgreich gespeichert.",
        "ajustes_aviso_reinicio": "Sprache erfolgreich aktualisiert.",
        
        # Household Confirmation Modal
        "hogar_titulo": "🏠 Sind Sie an Ihrem primären Lernort?",
        "hogar_subtitulo": "Standortkontrolle und Kontoschutz",
        "hogar_btn_temporal": "✈️ Unterwegs Lernen (Reise)",
        "hogar_btn_actualizar": "🏡 Dieses Netzwerk als primären Lernort festlegen",

        # What's New v1.6
        "modal_novedades_titulo": "🎉 Willkommen bei KernossAI v{version}!",
        "modal_novedades_subtitulo": "Entdecken Sie die neuen Funktionen und Verbesserungen dieser Version:",
        "modal_novedades_btn_empezar": "🚀 KernossAI Jetzt Starten!",
        "nov_item_soporte_tit": "🛡️ Offizieller E2EE-Support mit Kategorisierung",
        "nov_item_soporte_desc": "Direkter Chat-Kanal mit kernossai@support.com mit Themenauswahl (Fragen, KI, Fehler, Konten) und Antworten in Echtzeit.",
        "nov_item_multi_tit": "👥 Multi-Account-Manager in den Einstellungen",
        "nov_item_multi_desc": "Melden Sie sich mit mehreren Konten auf demselben PC an und wechseln Sie mit 1 Klick (🔄 Wechseln) ohne Passworteingabe.",
        "nov_item_rol_tit": "🎓 Akademische Rollenauswahl (Schüler / Lehrer)",
        "nov_item_rol_desc": "Wechseln Sie jederzeit in den Einstellungen Ihren Modus, um den Übungsersteller und Prüfungskorrektor ohne Neustart freizuschalten.",
        "nov_item_mod_tit": "⛔ Live-Moderationswächter & Sperrbildschirm",
        "nov_item_mod_desc": "Echtzeit-Erkennung von Sperren mit automatischem Logout, vollständiger Sperrung des KI-Zugriffs und rotem Informationsbildschirm.",
        "nov_item_cloud_tit": "⚡ Sitzungspersistenz & Supabase Cloud Storage",
        "nov_item_cloud_desc": "Sichere Verbindung zur Supabase-Cloud zur Vermeidung unbeabsichtigter Abmeldungen beim Neustart und dauerhafter Datenspeicherung.",
        "nov_item_hwid_tit": "💻 Hardware-Betrugsschutz (HWID)",
        "nov_item_hwid_desc": "Kryptografische Hardware-Geräteerkennung zum Schutz von Konten und zur Verhinderung von Missbrauch.",

        # OTA Update
        "ota_btn_actualizar": "⚡ Automatisch Aktualisieren (OTA)",
        "ota_btn_web": "🌐 Auf Website Herunterladen",
        "ota_descargando": "Update wird heruntergeladen...",
        "ota_instalando": "⚡ Update wird installiert und neu gestartet...",
        "ota_error": "Fehler beim Herunterladen: {err}",

        # Betreuung & Verknüpfung Schüler <-> Lehrer
        "btn_tutoria_alumno": "👨‍🏫 Mein Lehrer",
        "btn_tutoria_profesor": "🎓 Meine Schüler",
        "tutoria_modal_titulo_alumno": "👨‍🏫 Mein Betreuungslehrer & Fragen",
        "tutoria_modal_titulo_profesor": "🎓 Lehrerbereich: Schüler & Anfragen",
        "tutoria_tab_profesores": "👨‍🏫 Verfügbare Lehrer",
        "tutoria_tab_mi_profe": "💬 Chat mit meinem Lehrer",
        "tutoria_tab_solicitudes": "🔔 Ausstehende Anfragen",
        "tutoria_tab_alumnos": "👥 Meine verknüpften Schüler",
        "tutoria_btn_solicitar": "📨 Verknüpfung Anfragen",
        "tutoria_btn_aceptar": "✅ Schüler Annehmen",
        "tutoria_btn_rechazar": "❌ Ablehnen",
        "tutoria_btn_desvincular": "⚠️ Trennen",
        "tutoria_sin_profes": "Derzeit sind keine Lehrer registriert.",
        "tutoria_solicitud_pendiente": "⏳ Anfrage ausstehend bei Lehrer {nombre} ({email})",

        # Support E2EE
        "sop_titulo_ventana": "🛡️ Offizieller Support KernossAI — E2EE-Verschlüsselter Chat",
        "sop_subtitulo": "🔒 Ende-zu-Ende-Verschlüsselung (E2EE) Aktiv • Null Server-Kenntnis",
        "sop_aviso_beta": "🧪 Beta-Funktion • Probleme bitte auf GitHub melden",
        "sop_lbl_motivo": "📌 Grund / Thema:",
        "sop_plh_input": "Nachricht an den Support eingeben (wird vor dem Senden verschlüsselt)...",
        "sop_btn_enviar": "Senden 📤",

        # Module: Notenrechner
        "calc_titulo": "📊 Notenrechner & Gewichtung",
        "calc_subtitulo": "Noten organisieren, gewichten und visualisieren",
        "calc_lbl_materia": "Fach / Kurs",
        "calc_plh_materia": "z.B.: Mathematik, Physik...",
        "calc_lbl_nota": "Direkte Note (0-10)",
        "calc_plh_nota": "z.B.: 9.5",
        "calc_lbl_pct": "% der Gesamtnote (Gewichtung)",
        "calc_plh_pct": "z.B.: 40",
        "calc_btn_guardar_nota": "➕ Note Speichern",
        "calc_btn_bloques": "📂 Teilnoten / Blöcke Hinzufügen",
        "calc_hdr_registro": "Detailliertes Protokoll",
        "calc_hdr_grafica": "Leistungsdiagramm",
        "calc_btn_calcular": "⚡ Endnote Berechnen",
        "calc_btn_limpiar": "🗑️ Alles Löschen",
        "calc_btn_exportar": "📄 Bericht Exportieren",

        # Module: Notizen
        "apunt_titulo": "📝 Notizen & Word-Export",
        "apunt_subtitulo": "Ihre privaten Lernnotizen mit KI-Unterstützung",
        "apunt_btn_nueva": "➕ Neue Notiz",
        "apunt_btn_leer": "🔊 Vorlesen",
        "apunt_btn_guardar": "💾 Speichern",
        "apunt_btn_word": "📄 Word",
        "apunt_btn_borrar": "🗑️ Löschen",
        "apunt_lbl_sin_nota": "Wählen Sie eine Notiz",

        # Module: Zusammenfasser
        "resum_titulo": "🔍 KI-Text-Zusammenfasser",
        "resum_subtitulo": "Erstellen Sie strukturierte Zusammenfassungen beliebiger Themen",
        "resum_lbl_entrada": "Notizen oder Text hier einfügen:",
        "resum_lbl_salida": "KI-generierte Zusammenfassung:",
        "resum_btn_resumir": "⚡ Zusammenfassung Erstellen",
        "resum_btn_limpiar": "🗑️ Löschen",
        "resum_btn_copiar": "📋 Kopieren",

        # Module: Prüfungsgenerator
        "exam_titulo": "🎯 Prüfungs- & Quiz-Generator",
        "exam_subtitulo": "Erstellen Sie Prüfungen aus Ihren Lerninhalten",
        "exam_lbl_tema": "Prüfungsthema oder Inhalt:",
        "exam_lbl_tipo": "Prüfungsformat:",
        "exam_lbl_preguntas": "Anzahl der Fragen:",
        "exam_lbl_dificultad": "Schwierigkeit:",
        "exam_btn_generar": "⚡ Prüfung Generieren",

        # Module: Problem-Löser
        "ayud_titulo": "🤖 KI-Problem-Löser & Studienassistent",
        "ayud_subtitulo": "Schritt-für-Schritt-Lösungen für Mathematik, Wissenschaft und Code",
        "ayud_lbl_enunciado": "Geben Sie Ihre Aufgabe oder Übung ein:",
        "ayud_lbl_solucion": "Lösung & Schritt-für-Schritt-Erklärung:",
        "ayud_btn_resolver": "⚡ Schritt für Schritt Lösen",

        # Module: Mindmaps
        "mapa_titulo": "🧠 KI-Mindmap-Generator",
        "mapa_subtitulo": "Visualisieren Sie die Begriffshierarchie beliebiger Themen",
        "mapa_lbl_tema": "Hauptbegriff oder Thema:",
        "mapa_btn_generar": "⚡ Mindmap Generieren",

        # Module: Studienplaner
        "agenda_titulo": "📅 Studienplaner & Kalender",
        "agenda_subtitulo": "Organisieren Sie Abgaben, Prüfungen und Lerneinheiten",
        "agenda_btn_anadir": "➕ Aufgabe / Prüfung Hinzufügen",

        # Teacher Module: Übungsersteller
        "cread_titulo": "✏️ Übungsersteller & Bewertungsraster",
        "cread_subtitulo": "Erstellen Sie maßgeschneiderte Aufgaben mit Musterlösungen",
        "cread_btn_generar": "⚡ Übungen Generieren",

        # Teacher Module: Prüfungskorrektor
        "corr_titulo": "📋 Automatischer Prüfungskorrektor",
        "corr_subtitulo": "Schülerantworten analysieren und pädagogisches Feedback generieren",
        "corr_btn_corregir": "⚡ Korrigieren & Bewerten"
    },

    "fr": {
        # General & App
        "app_nombre": "⚡ KernossAI",
        "app_subtitulo": "Suite d'Étude & d'Éducation Propulsée par l'IA",
        "app_tagline": "Suite d'Étude 2026",
        "btn_novedades": "✨ Nouveautés v1.6",
        "btn_ajustes": "⚙️ Paramètres / Config",
        "btn_cerrar_sesion": "🚪 Déconnexion",
        "lbl_rol_alumno": "Élève / Étudiant",
        "lbl_rol_profesor": "Professeur",
        "lbl_selecciona_idioma": "🌐 Langue / Language :",
        
        # Login & Register
        "tab_login": "Connexion",
        "tab_registro": "S'inscrire",
        "lbl_email": "Adresse e-mail",
        "placeholder_email": "vous@email.fr",
        "lbl_pass": "Mot de passe",
        "placeholder_pass": "••••••••",
        "placeholder_pass_reg": "Minimum 6 caractères",
        "lbl_nombre": "Nom complet",
        "placeholder_nombre": "Votre nom",
        "lbl_rol": "Rôle",
        "btn_login": "Connexion",
        "btn_registro": "Créer un Compte",
        "login_conectando": "Connexion au serveur...",
        "reg_creando": "Création du compte sur le serveur...",
        "login_error_campos": "Veuillez remplir tous les champs.",
        "login_error_correo": "Adresse e-mail invalide.",
        "login_error_pass_len": "Le mot de passe doit comporter au moins 6 caractères.",
        "login_privacidad": "🔒 100% Gratuit & Privé • Vos notes restent sur votre ordinateur.",
        
        # Sidebar & Navigation
        "btn_home": "🏠  Accueil / Chat IA",
        "hdr_historial": "🕒 HISTORIQUE DE CHAT",
        "btn_nuevo_chat": "➕ Nouveau",
        "hdr_modulos_estudio": "MODULES D'ÉTUDE",
        "hdr_herramientas_docente": "OUTILS ENSEIGNANT",
        
        # Modules Sidebar
        "mod_mapas": "🧠 Cartes Mentales",
        "mod_calculador": "📊 Calculateur de Moyennes",
        "mod_apuntador": "📝 Prise de Notes & Word",
        "mod_resumidor": "🔍 Résumeur de Texte IA",
        "mod_examenes": "🎯 Générateur d'Examens",
        "mod_ayudante": "🤖 Résolveur de Problèmes",
        "mod_agenda": "📅 Agenda d'Études",
        "mod_ejercicios": "✏️ Créateur d'Exercices",
        "mod_corrector": "📋 Correcteur d'Examens",
        "mod_soporte": "🛡️ Support Officiel & Messages E2EE",
        "btn_admin_panel": "👑 Panneau de Modération & Bans",
        
        # Home & Chat
        "home_bienvenida": "Bienvenue, {rol} {nombre} !",
        "home_estado_ia": "🟢 Assistant IA Actif (Groq & Gemini) • Que voulez-vous étudier aujourd'hui ?",
        "home_placeholder_input": "Tapez votre question, sujet d'examen ou problème pour l'IA...",
        "btn_consultar_ia": "⚡ Consulter l'IA",
        "btn_escuchar": "🔊 Écouter",
        "btn_word": "📄 Word",
        "opt_groq": "⚡ Groq (Rapide)",
        "opt_gemini": "🧠 Gemini (Approfondi)",
        "btn_detener_audio": "⏹ Arrêter",
        
        # Settings
        "ajustes_titulo": "⚙️ Paramètres & Configuration",
        "ajustes_subtitulo": "Personnalisez la langue, la voix de lecture (TTS) et les préférences",
        "ajustes_sec_idioma": "🌐 Langue de l'Application",
        "ajustes_lbl_idioma": "Sélectionnez la langue de l'interface :",
        "ajustes_sec_rol": "🎓 Mode et Rôle du Compte",
        "ajustes_lbl_rol": "Mode de travail actif :",
        "ajustes_sec_multi": "👥 Gestionnaire Multi-Comptes",
        "ajustes_btn_agregar_cuenta": "➕ Se Connecter à un Autre Compte",
        "ajustes_sec_voz": "🔊 Lecture à Voix Haute (TTS)",
        "ajustes_lbl_voz": "Voix de lecture :",
        "ajustes_lbl_velocidad": "Vitesse :",
        "ajustes_btn_probar": "🔊 Tester la Voix",
        "ajustes_sec_privacidad": "⚠️ Zone de Confidentialité — Compte",
        "ajustes_btn_borrar_cuenta": "🗑️ Supprimer Définitivement Mon Compte",
        "ajustes_btn_guardar": "💾 Enregistrer les Paramètres",
        "ajustes_btn_cancelar": "Annuler",
        "ajustes_guardado_ok": "Paramètres enregistrés avec succès.",
        "ajustes_aviso_reinicio": "Langue mise à jour avec succès.",
        
        # Household Confirmation Modal
        "hogar_titulo": "🏠 Êtes-vous à votre Lieu d'Étude Principal ?",
        "hogar_subtitulo": "Contrôle de localisation et protection du compte partagé",
        "hogar_btn_temporal": "✈️ Étudier en Déplacement (Voyage)",
        "hogar_btn_actualizar": "🏡 Définir ce Réseau comme Domicile Principal",

        # What's New v1.6
        "modal_novedades_titulo": "🎉 Bienvenue dans KernossAI v{version} !",
        "modal_novedades_subtitulo": "Découvrez les nouvelles fonctionnalités et améliorations ajoutées dans cette version :",
        "modal_novedades_btn_empezar": "🚀 Commencer à Utiliser KernossAI !",
        "nov_item_soporte_tit": "🛡️ Support Technique Officiel E2EE avec Catégorisation",
        "nov_item_soporte_desc": "Canal de discussion direct et chiffré avec kernossai@support.com avec sélecteur de motif (doutes, IA, bugs, comptes) et respuestas en direct.",
        "nov_item_multi_tit": "👥 Gestionnaire Multi-Comptes dans les Paramètres",
        "nov_item_multi_desc": "Connectez-vous avec plusieurs comptes sur le même ordinateur et passez de l'un à l'autre en 1 clic (🔄 Changer) sans retaper les mots de passe.",
        "nov_item_rol_tit": "🎓 Sélecteur de Rôle Académique (Élève / Professeur)",
        "nov_item_rol_desc": "Changez de mode à tout moment dans les Paramètres pour débloquer le Créateur d'Exercices et le Correcteur d'Examens sans redémarrer.",
        "nov_item_mod_tit": "⛔ Vigile de Modération en Direct & Écran de Blocage",
        "nov_item_mod_desc": "Détection instantanée des sanctions en temps réel avec déconnexion automatique, révocation totale de l'accès à l'IA et écran rouge d'avertissement.",
        "nov_item_cloud_tit": "⚡ Persistance de Session & Stockage Cloud Supabase",
        "nov_item_cloud_desc": "Connexion sécurisée au cloud Supabase pour éviter les déconnexions intempestives lors du redémarrage et conserver les données de façon permanente.",
        "nov_item_hwid_tit": "💻 Protection Anti-Fraude Matérielle (HWID)",
        "nov_item_hwid_desc": "Empreinte matérielle cryptographique pour protéger les comptes et prévenir les abus d'accès.",

        # OTA Update
        "ota_btn_actualizar": "⚡ Mettre à Jour Automatiquement (OTA)",
        "ota_btn_web": "🌐 Télécharger sur le Web",
        "ota_descargando": "Téléchargement de la mise à jour...",
        "ota_instalando": "⚡ Installation de la mise à jour et redémarrage...",
        "ota_error": "Erreur lors du téléchargement : {err}",

        # Tutorat & Liaison Élève <-> Professeur
        "btn_tutoria_alumno": "👨‍🏫 Mon Professeur",
        "btn_tutoria_profesor": "🎓 Mes Élèves",
        "tutoria_modal_titulo_alumno": "👨‍🏫 Mon Professeur Tuteur & Questions",
        "tutoria_modal_titulo_profesor": "🎓 Espace Tutorat : Élèves & Demandes",
        "tutoria_tab_profesores": "👨‍🏫 Professeurs Disponibles",
        "tutoria_tab_mi_profe": "💬 Chat avec mon Professeur",
        "tutoria_tab_solicitudes": "🔔 Demandes en Attente",
        "tutoria_tab_alumnos": "👥 Mes Élèves Connectés",
        "tutoria_btn_solicitar": "📨 Demander la Connexion",
        "tutoria_btn_aceptar": "✅ Accepter l'Élève",
        "tutoria_btn_rechazar": "❌ Refuser",
        "tutoria_btn_desvincular": "⚠️ Déconnecter",
        "tutoria_sin_profes": "Aucun professeur inscrit pour le moment.",
        "tutoria_solicitud_pendiente": "⏳ Demande en attente auprès du professeur {nombre} ({email})",

        # Support E2EE
        "sop_titulo_ventana": "🛡️ Support Officiel KernossAI — Chat Chiffré E2EE",
        "sop_subtitulo": "🔒 Chiffrement de Bout en Bout (E2EE) Actif • Zéro Connaissance Serveur",
        "sop_aviso_beta": "🧪 Fonction bêta • Signalez tout problème sur GitHub",
        "sop_lbl_motivo": "📌 Motif / Sujet :",
        "sop_plh_input": "Tapez votre message au support (chiffré avant l'envoi)...",
        "sop_btn_enviar": "Envoyer 📤",

        # Module: Calculateur de Moyennes
        "calc_titulo": "📊 Calculateur de Moyennes Pondérées",
        "calc_subtitulo": "Organisez, pondérez et visualisez vos notes",
        "calc_lbl_materia": "Matière ou Cours",
        "calc_plh_materia": "ex : Mathématiques, Physique...",
        "calc_lbl_nota": "Note Directe (0-10)",
        "calc_plh_nota": "ex : 9.5",
        "calc_lbl_pct": "% du Total (Pondération)",
        "calc_plh_pct": "ex : 40",
        "calc_btn_guardar_nota": "➕ Enregistrer la Note",
        "calc_btn_bloques": "📂 Ajouter Sous-notes / Blocs",
        "calc_hdr_registro": "Registre Détaillé",
        "calc_hdr_grafica": "Graphique de Performance",
        "calc_btn_calcular": "⚡ Calculer la Moyenne Finale",
        "calc_btn_limpiar": "🗑️ Tout Effacer",
        "calc_btn_exportar": "📄 Exporter le Rapport",

        # Module: Prise de Notes
        "apunt_titulo": "📝 Prise de Notes & Export Word",
        "apunt_subtitulo": "Vos notes de cours privées avec assistance IA",
        "apunt_btn_nueva": "➕ Nouvelle Note",
        "apunt_btn_leer": "🔊 Écouter",
        "apunt_btn_guardar": "💾 Enregistrer",
        "apunt_btn_word": "📄 Word",
        "apunt_btn_borrar": "🗑️ Supprimer",
        "apunt_lbl_sin_nota": "Sélectionnez une note",

        # Module: Résumeur IA
        "resum_titulo": "🔍 Résumeur de Texte IA",
        "resum_subtitulo": "Générez des résumés structurés de n'importe quel cours",
        "resum_lbl_entrada": "Collez vos notes ou votre texte ici :",
        "resum_lbl_salida": "Résumé Rigoureux Généré par l'IA :",
        "resum_btn_resumir": "⚡ Générer le Résumé avec l'IA",
        "resum_btn_limpiar": "🗑️ Effacer",
        "resum_btn_copiar": "📋 Copier",

        # Module: Générateur d'Examens
        "exam_titulo": "🎯 Générateur d'Examens & Quiz",
        "exam_subtitulo": "Créez des examens à partir de vos sujets d'étude",
        "exam_lbl_tema": "Sujet ou Contenu de l'Examen :",
        "exam_lbl_tipo": "Format d'Examen :",
        "exam_lbl_preguntas": "Nombre de Questions :",
        "exam_lbl_dificultad": "Difficulté :",
        "exam_btn_generar": "⚡ Générer l'Examen avec l'IA",

        # Module: Résolveur de Problèmes
        "ayud_titulo": "🤖 Résolveur de Problèmes & Assistant IA",
        "ayud_subtitulo": "Solutions pas à pas pour les maths, sciences et programmation",
        "ayud_lbl_enunciado": "Entrez l'énoncé de votre problème ou exercice :",
        "ayud_lbl_solucion": "Solution & Explication Pas à Pas :",
        "ayud_btn_resolver": "⚡ Résoudre Pas à Pas",

        # Module: Cartes Mentales
        "mapa_titulo": "🧠 Générateur de Cartes Mentales IA",
        "mapa_subtitulo": "Visualisez la hiérarchie conceptuelle de n'importe quel cours",
        "mapa_lbl_tema": "Concept Principal ou Sujet d'Étude :",
        "mapa_btn_generar": "⚡ Générer la Carte Mentale",

        # Module: Agenda d'Études
        "agenda_titulo": "📅 Agenda & Planificateur d'Études",
        "agenda_subtitulo": "Organisez vos échéances, examens et sessions de révision",
        "agenda_btn_anadir": "➕ Ajouter Tâche / Examen",

        # Teacher Module: Créateur d'Exercices
        "cread_titulo": "✏️ Créateur d'Exercices & Barèmes pour Enseignants",
        "cread_subtitulo": "Concevez des activités personnalisées avec corrigés",
        "cread_btn_generar": "⚡ Générer les Exercices",

        # Teacher Module: Correcteur d'Examens
        "corr_titulo": "📋 Correcteur d'Examens Automatisé",
        "corr_subtitulo": "Analysez les réponses des élèves et générez un retour pédagogique",
        "corr_btn_corregir": "⚡ Corriger et Évaluer"
    }
}

# Idioma activo en tiempo de ejecución
_IDIOMA_ACTUAL = "es"

def fijar_idioma(codigo: str):
    """Establece el idioma activo para la sesión actual."""
    global _IDIOMA_ACTUAL
    if codigo in TRADUCCIONES:
        _IDIOMA_ACTUAL = codigo
    else:
        _IDIOMA_ACTUAL = "es"

def obtener_idioma_activo() -> str:
    """Devuelve el código del idioma actual ('es', 'en', 'de', 'fr')."""
    return _IDIOMA_ACTUAL

def t(clave: str, **kwargs) -> str:
    """
    Obtiene la traducción de una clave en el idioma activo.
    Permite formatear variables (ej: t('home_bienvenida', rol='Alumno', nombre='Usuario')).
    """
    lang_dict = TRADUCCIONES.get(_IDIOMA_ACTUAL, TRADUCCIONES["es"])
    texto = lang_dict.get(clave, TRADUCCIONES["es"].get(clave, clave))
    if kwargs:
        try:
            return texto.format(**kwargs)
        except Exception:
            return texto
    return texto
