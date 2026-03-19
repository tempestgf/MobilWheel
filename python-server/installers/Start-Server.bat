@echo off
REM ============================================================================
REM Mobile Wheel Server - Quick Setup
REM Configuración rápida de vJoy before starting the server
REM ============================================================================

setlocal enabledelayedexpansion

cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║    🎮 Mobile Wheel Server - Setup Wizard                      ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python no está instalado
    echo.
    echo El servidor requiere Python para ejecutarse.
    echo Descárgalo desde: https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo ✓ Python detectado
echo.

REM Obtener la ruta del directorio actual
set SCRIPT_DIR=%~dp0

echo Verificando estado de vJoy...
python -c "from vjoy_setup_helper import VjoySetupHelper; h = VjoySetupHelper(); print('Status: ' + h.check_vjoy_status())" >nul 2>&1

echo.
echo Opciones:
echo.
echo 1) Instalar vJoy ahora
echo 2) Iniciar servidor sin instalar vJoy
echo 3) Salir
echo.

set /p choice="Selecciona una opción (1-3): "

if "%choice%"=="1" (
    echo.
    call "%SCRIPT_DIR%install_vjoy.bat"
    if errorlevel 1 (
        exit /b 1
    )
) else if "%choice%"=="2" (
    echo Continuando sin vJoy...
) else if "%choice%"=="3" (
    exit /b 0
) else (
    echo Opción no válida
    pause
    exit /b 1
)

echo.
echo ✓ Setup completado. Iniciando servidor...
echo.

REM Iniciar el servidor
python "%SCRIPT_DIR%ServerApp.py"
