# 📦 Instalador Automático de vJoy

## ¿Qué es vJoy?

**vJoy** es un driver que emula controles de videojuegos en Windows. Es esencial para que el servidor de Mobile Wheel pueda enviar comandos de control a tu aplicación de carrera.

- **Descarga oficial**: https://www.vjoy.org/
- **Versión**: 2.2.1.1
- **Arquitecturas soportadas**: x86 (32-bit) y x64 (64-bit)

## 🚀 Instalación Rápida

### Opción 1: Ejecutable por lotes (Recomendado para principiantes)

1. **Haz doble clic** en: `install_vjoy.bat`
2. El script descargará e instalará vJoy automáticamente
3. Se te pedirá confirmación de que quieres instalar vJoy
4. ✅ ¡Listo!

### Opción 2: PowerShell (Avanzados)

1. **Abre PowerShell** como Administrador
2. Navega a la carpeta del servidor Python:
   ```powershell
   cd "C:\ruta\a\python-server"
   ```
3. Ejecuta:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   ./Install-vJoy.ps1
   ```
4. ✅ ¡Listo!

### Opción 3: Línea de comandos (Avanzados)

1. **Abre CMD** como Administrador
2. Navega a la carpeta del servidor Python:
   ```cmd
   cd C:\ruta\a\python-server
   ```
3. Ejecuta:
   ```cmd
   python vjoy_installer.py
   ```

## 🔍 Diagnóstico

### Verificar si vJoy está instalado

```python
from vjoy_setup_helper import VjoySetupHelper

helper = VjoySetupHelper()
status = helper.check_vjoy_status()

if status == 'installed':
    print("✓ vJoy está instalado")
elif status == 'downloaded':
    print("⚙️ vJoy está descargado pero no instalado")
else:
    print("✗ vJoy no encontrado")
```

### Detectar arquitectura del sistema

```python
from vjoy_setup_helper import VjoySetupHelper

helper = VjoySetupHelper()
print(f"Arquitectura: {helper.get_architecture()}")  # x86 o x64
```

## 📁 Estructura de Carpetas

Después de la instalación, la carpeta `vJoy` se verá así:

```
vJoy/
├── x86/
│   └── vJoy_Setup.exe (instalador 32-bit)
└── x64/
    └── vJoy_Setup.exe (instalador 64-bit)
```

## ⚙️ Integración Programática

### Usar en tu código Python

```python
from vjoy_setup_helper import ensure_vjoy_installed

# Asegurar que vJoy esté instalado
ensure_vjoy_installed()

# Con callbacks para actualizar la UI
def status_callback(status, message):
    print(f"[{status}] {message}")

ensure_vjoy_installed(ui_callback=status_callback)
```

### Integración en PyQt5 (como en ServerApp.py)

```python
from vjoy_setup_helper import VjoySetupHelper

class ServerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... tu código ...
        self.setup_vjoy()
    
    def setup_vjoy(self):
        """Verifica e instala vJoy si es necesario"""
        helper = VjoySetupHelper()
        
        if helper.needs_installation():
            self.log_message("Instalando vJoy...")
            
            def on_progress(percent):
                self.progress_bar.setValue(percent)
            
            def on_install_status(message):
                self.log_message(message)
            
            def on_complete(success):
                if success:
                    self.log_message("✓ vJoy instalado correctamente")
                else:
                    self.log_message("✗ Error installing vJoy")
            
            helper.install_async(on_progress, on_install_status, on_complete)
        else:
            self.log_message("✓ vJoy ya está instalado")
```

## 🔐 Permisos Requeridos

- Se requieren **derechos de administrador** para instalar vJoy
- El instalador solicitará confirmación automáticamente
- Si ejecutas desde una línea de comandos, asegúrate de ejecutarla como Administrador

## 🐛 Solución de Problemas

### Problema: "Python no está instalado"

**Solución**: Descarga Python desde https://www.python.org/
- Asegúrate de marcar "Add Python to PATH" durante la instalación
- Reinicia el sistema después de instalar Python

### Problema: "Acceso denegado"

**Solución**:
1. Cierra todos los programas que usen vJoy
2. Ejecuta el instalador como Administrador
3. Desactiva temporalmente el antivirus (algunas veces interfiere)

### Problema: "No se puede descargar vJoy"

**Solución**:
1. Verifica tu conexión a Internet
2. Comprueba que el sitio https://www.vjoy.org/ está accesible
3. Descarga vJoy manualmente desde: https://www.vjoy.org/dl/vJoy-2.2.1.1.zip
4. Extrae el contenido en la carpeta `vJoy/` del servidor

### Problema: "El instalador falló"

**Solución**:
1. Verifica que tu antivirus no bloquea la descarga
2. Prueba deshabilitando temporalmente el antivirus
3. Intenta instalar vJoy manualmente desde: https://www.vjoy.org/

## 📊 Logs y Debugging

Los logs se guardan en:
- Consola de Python durante la ejecución
- Historial de instalación en la carpeta `vJoy/`

Para ver logs detallados desde Python:

```python
import logging
from vjoy_installer import logger

# Mostrar todos los logs
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
```

## 🔄 Actualizar vJoy

Para actualizar a una versión más nueva:

1. Elimina la carpeta `vJoy/` completamente
2. Ejecuta el instalador nuevamente
3. Se descargará la versión más reciente

## 📝 Notas Técnicas

- El instalador detecta automáticamente si el sistema es x86 o x64
- Descarga la versión apropiada automáticamente
- El archivo ZIP se descarga en caché y se organiza por arquitectura
- La instalación es **silenciosa** (sin popups durante el proceso)

## ✅ Verificación Final

Después de instalar vJoy, verifica que funciona:

```python
try:
    import pyvjoy
    print("✓ pyvJoy cargado correctamente")
    
    # Intentar crear un joystick virtual
    j = pyvjoy.VJoyDevice(1)
    print(f"✓ Joystick virtual creado")
    j.reset()
except Exception as e:
    print(f"✗ Error: {e}")
```

## ❓ Soporte

Si tienes problemas:
- Consulta la web oficial: https://www.vjoy.org/
- Verifica los logs en la consola
- Intenta instalar vJoy manualmente desde el sitio oficial

---

**Última actualización**: 2026
**Versión soportada**: vJoy 2.2.1.1
