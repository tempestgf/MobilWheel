@echo off
REM ============================================================================
REM vJoy Automatic Installer for Mobile Wheel Server
REM ============================================================================
REM Este script descarga e instala vJoy automáticamente
REM Requiere Python instalado en el sistema
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║      vJoy Automatic Installer - Mobile Wheel Server       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ ERROR: Python no está instalado o no está en la ruta del sistema
    echo.
    echo Por favor, instale Python desde: https://www.python.org/
    echo Asegúrese de marcar "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

echo ✓ Python detectado
echo.

REM Obtener la ruta del directorio actual
set SCRIPT_DIR=%~dp0

echo 📁 Ruta del servidor: %SCRIPT_DIR%
echo.

REM Ejecutar el instalador de vJoy
echo ⚙️  Iniciando instalador de vJoy...
echo.

python "%SCRIPT_DIR%vjoy_installer.py"

if errorlevel 1 (
    echo.
    echo ✗ La instalación de vJoy falló
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✓ vJoy instalado correctamente                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Presione cualquier tecla para continuar...
pause >nul
