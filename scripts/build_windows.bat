@echo off
REM ─────────────────────────────────────────────────────────────
REM KernossAI — Compilador para Windows (.exe y Setup)
REM ─────────────────────────────────────────────────────────────

echo ============================================================
echo   KernossAI — Compilacion para Windows (64-bit)
echo ============================================================
echo.

echo [1/3] Verificando e instalando dependencias de Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo [2/3] Compilando ejecutable nativo (.exe) con PyInstaller...
python build_desktop.py

echo.
echo [3/3] Comprobando Inno Setup para crear instalador (.exe Setup)...
set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if exist "%ISCC_PATH%" (
    echo Compilando Setup con Inno Setup...
    "%ISCC_PATH%" installer_windows.iss
    echo.
    echo ============================================================
    echo   Instalador generado con exito en:
    echo   dist\installer\KernossAI_Setup_v1.8.exe
    echo ============================================================
) else (
    echo [AVISO] Inno Setup no encontrado en las rutas por defecto.
    echo El ejecutable portable esta listo en: dist\KernossAI\KernossAI.exe
    echo Para compilar el Setup (.exe instalador), instala Inno Setup 6 y ejecuta:
    echo ISCC installer_windows.iss
)

echo.
pause
