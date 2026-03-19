# 🚀 Guía de Inicio Rápido - vJoy Installer

## Opción Más Fácil (Recomendada)

### Para Usuarios Principiantes

1. **Abre la carpeta** del servidor Python
2. **Haz doble clic** en uno de estos archivos:
   - `install_vjoy.bat` - Si prefieres simplemente instalar vJoy
   - `Start-Server.bat` - Si quieres instalar vJoy E iniciar el servidor

¡Eso es todo! El proceso es completamente automático.

---

## ¿Qué hacen estos archivos?

| Archivo | Propósito |
|---------|----------|
| **install_vjoy.bat** | ⬇️ Descarga e instala vJoy únicamente |
| **Start-Server.bat** | ⬇️ Descarga vJoy (si es necesario) E inicia el servidor |
| **Install-vJoy.ps1** | Para usuarios avanzados de PowerShell |

---

## Flujo de Instalación

```
┌─────────────────────────────────────┐
│  Ejecutar install_vjoy.bat          │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  ¿Está instalado en el sistema?     │
│  (verificar registro de Windows)    │
└────────┬────────────────┬───────────┘
         │                │
      SÍ │                │ NO
         │                │
         ▼                ▼
    ✓LISTO            ┌───────────────────┐
                      │ ¿Está descargado? │
                      └────┬───────┬──────┘
                           │       │
                        SÍ │       │ NO
                           │       │
                           ▼       ▼
                        INSTALAR  ┌──────────────────┐
                                  │ DESCARGAR ZIP    │
                                  │ (desde internet) │
                                  └────┬─────────────┘
                                       │
                                       ▼
                                  ┌──────────────────┐
                                  │ EXTRAER ARCHIVOS │
                                  └────┬─────────────┘
                                       │
                                       ▼
                                  ┌──────────────────┐
                                  │ INSTALAR vJoy    │
                                  │ (con privilegios)│
                                  └────┬─────────────┘
                                       │
                                       ▼
                                  ✓ COMPLETADO
```

---

## Requisitos Previos

### ✓ Python 3.7+

Verifica que Python esté instalado:

```cmd
python --version
```

Si no ves una versión, descarga Python desde: https://www.python.org/

**IMPORTANTE**: Al instalar Python, marca esta opción:
- ☑️ "Add Python to PATH"

---

## Diagnóstico Rápido

### Verificar que vJoy está instalado

Abre PowerShell o CMD y ejecuta:

```python
python -c "from vjoy_setup_helper import VjoySetupHelper; print(VjoySetupHelper().check_vjoy_status())"
```

Debería salir: `installed`

### Ver arquitectura del sistema

```python
python -c "from vjoy_setup_helper import VjoySetupHelper; print(VjoySetupHelper().get_architecture())"
```

Debería salir: `x64` o `x86`

---

## 🔧 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| El archivo .bat no abre | Descarga Python: https://www.python.org/ |
| "Acceso denegado" | Ejecuta como Administrador (click derecho) |
| "No se puede conectar" | Verifica tu WiFi/Conexión a Internet |
| El archivo ZIP no descarga | Descárgalo manualmente: https://www.vjoy.org/dl/vJoy-2.2.1.1.zip |

---

## 📝 Archivos Importantes

```
python-server/
├── install_vjoy.bat          👈 Ejecuta esto para instalar vJoy
├── Start-Server.bat          👈 Ejecuta esto para instalar + servidor
├── Install-vJoy.ps1          👈 Versión PowerShell
├── vjoy_installer.py         ⚙️  Módulo de descarga/instalación
├── vjoy_setup_helper.py      🔧 Utilidades para integración
├── VJOY_INSTALLER_README.md  📖 Guía completa (este archivo)
└── vJoy/                     📁 Carpeta de instalaciones
    ├── x86/                  (instalador 32-bit)
    └── x64/                  (instalador 64-bit)
```

---

## 🎯 Próximos Pasos

Una vez que vJoy esté instalado:

1. ✅ El servidor puede usar controles virtuales
2. ✅ Tu aplicación móvil puede enviar comandos
3. ✅ Los videojuegos recibirán los controles

---

## 💡 Pro Tips

### Ejecutar sin interfaz gráfica

```cmd
install_vjoy.bat
REM ... O ...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; ./Install-vJoy.ps1 -Silent"
```

### Integrar en tus scripts

```python
from vjoy_setup_helper import ensure_vjoy_installed

# En tu código principal
ensure_vjoy_installed()

# Ahora puedes usar vJoy
import pyvjoy
j = pyvjoy.VJoyDevice(1)
```

### Ver logs detallados

```cmd
python -v vjoy_installer.py
```

---

## ❓ ¿Necesitas Ayuda?

1. **Lee** [VJOY_INSTALLER_README.md](VJOY_INSTALLER_README.md) - Guía completa
2. **Consulta** https://www.vjoy.org/ - Sitio oficial
3. **Verifica** que Python esté correctamente instalado

---

**¡Listo para empezar!** 🎮
