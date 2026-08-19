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
        
        # Módulos
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
        "ajustes_sec_voz": "🔊 Lector en Voz Alta con IA (TTS)",
        "ajustes_lbl_voz": "Voz de Lectura:",
        "ajustes_lbl_velocidad": "Velocidad:",
        "ajustes_btn_probar": "🔊 Probar Voz",
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
        "nov_item_hwid_desc": "Identificación criptográfica de dispositivos para garantizar la seguridad de cuentas y prevenir el abuso de accesos."
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
        
        # Modules
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
        "ajustes_sec_voz": "🔊 AI Voice Reader (TTS)",
        "ajustes_lbl_voz": "Reading Voice:",
        "ajustes_lbl_velocidad": "Speed:",
        "ajustes_btn_probar": "🔊 Test Voice",
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
        "nov_item_hwid_desc": "Cryptographic hardware device fingerprinting to protect accounts and prevent unauthorized abuse."
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
        
        # Modules
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
        "ajustes_sec_voz": "🔊 KI-Sprachausgabe (TTS)",
        "ajustes_lbl_voz": "Vorlesestimme:",
        "ajustes_lbl_velocidad": "Geschwindigkeit:",
        "ajustes_btn_probar": "🔊 Stimme Testen",
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
        "nov_item_hwid_desc": "Kryptografische Hardware-Geräteerkennung zum Schutz von Konten und zur Verhinderung von Missbrauch."
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
        
        # Modules
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
        "ajustes_sec_voz": "🔊 Lecture à Voix Haute (TTS)",
        "ajustes_lbl_voz": "Voix de lecture :",
        "ajustes_lbl_velocidad": "Vitesse :",
        "ajustes_btn_probar": "🔊 Tester la Voix",
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
        "nov_item_soporte_desc": "Canal de discussion direct et chiffré avec kernossai@support.com avec sélecteur de motif (doutes, IA, bugs, comptes) et réponses en direct.",
        "nov_item_multi_tit": "👥 Gestionnaire Multi-Comptes dans les Paramètres",
        "nov_item_multi_desc": "Connectez-vous avec plusieurs comptes sur le même ordinateur et passez de l'un à l'autre en 1 clic (🔄 Changer) sans retaper les mots de passe.",
        "nov_item_rol_tit": "🎓 Sélecteur de Rôle Académique (Élève / Professeur)",
        "nov_item_rol_desc": "Changez de mode à tout moment dans les Paramètres pour débloquer le Créateur d'Exercices et le Correcteur d'Examens sans redémarrer.",
        "nov_item_mod_tit": "⛔ Vigile de Modération en Direct & Écran de Blocage",
        "nov_item_mod_desc": "Détection instantanée des sanctions en temps réel avec déconnexion automatique, révocation totale de l'accès à l'IA et écran rouge d'avertissement.",
        "nov_item_cloud_tit": "⚡ Persistance de Session & Stockage Cloud Supabase",
        "nov_item_cloud_desc": "Connexion sécurisée au cloud Supabase pour éviter les déconnexions intempestives lors du redémarrage et conserver les données de façon permanente.",
        "nov_item_hwid_tit": "💻 Protection Anti-Fraude Matérielle (HWID)",
        "nov_item_hwid_desc": "Empreinte matérielle cryptographique pour protéger les comptes et prévenir les abus d'accès."
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
