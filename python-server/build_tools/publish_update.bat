@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
  echo Uso:
  echo   publish_update.bat "ruta_instalador.exe" version "notas de version"
  echo Ejemplo:
  echo   publish_update.bat "dist\MobileWheelServer-1.0.1-setup.exe" 1.0.1 "Fixes y mejoras"
  exit /b 1
)

if "%~2"=="" (
  echo Falta version
  exit /b 1
)

set INSTALLER=%~1
set VERSION=%~2
set NOTES=%~3

if "%NOTES%"=="" set NOTES=Mejoras de estabilidad.

python "%~dp0publish_update.py" --installer "%INSTALLER%" --version "%VERSION%" --notes "%NOTES%" --set-app-version
if errorlevel 1 (
  echo Error publicando update
  exit /b 1
)

echo.
echo Update generado correctamente.
echo Siguiente paso: desplegar mobilwheelwebsite a produccion.
