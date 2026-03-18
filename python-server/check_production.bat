@echo off
REM PRODUCTION VERIFICATION SCRIPT
REM Verificación rápida de que todo está listo para producción
REM

setlocal enabledelayedexpansion

color 0A
cls

echo.
echo ========================================================================
echo        vJoy Installer - PRODUCTION READINESS VERIFICATION
echo ========================================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado
    echo.
    echo Descárgalo desde: https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [✓] Python detectado

REM Ejecutar production check
echo.
echo [INFO] Ejecutando verificación de producción...
echo.

python production_check.py

if errorlevel 1 (
    echo.
    echo [ERROR] Verificación falló
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo [✓] SISTEMA LISTO PARA PRODUCCIÓN
echo ========================================================================
echo.
echo Próximos pasos:
echo  1. Abrir: PRODUCTION_READY.md
echo  2. Abrir: DEPLOYMENT_GUIDE.md
echo  3. Distribuir a QA para testing
echo.
pause
