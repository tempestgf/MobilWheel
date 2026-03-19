# 🎮 vJoy Automatic Installer

Instalador automático y completamente integrado de vJoy para el servidor de Mobile Wheel.

## 🚀 Inicio Rápido

### Para Usuarios Finales (Más Fácil)

1. **Haz doble clic** en `install_vjoy.bat` o `Start-Server.bat`
2. El proceso es completamente automático
3. ✅ ¡Listo!

### Para Desarrolladores

```python
from vjoy_setup_helper import ensure_vjoy_installed

# Instalar automáticamente
ensure_vjoy_installed()

# Ahora puedes usar vJoy
import pyvjoy
j = pyvjoy.VJoyDevice(1)
```

## 📂 Estructura de Archivos Creados

### Archivos Principales

| Archivo | Tipo | Propósito |
|---------|------|----------|
| `vjoy_installer.py` | 🐍 Módulo Python | Descarga e instala vJoy desde internet |
| `vjoy_setup_helper.py` | 🐍 Módulo Python | Helper utilities para integración |
| `vjoy_bootstrap.py` | 🐍 Módulo Python | Integración con PyQt5 |
| `install_vjoy.bat` | 📜 Script Batch | Ejecutable para usuarios (Windows) |
| `Install-vJoy.ps1` | ⚡ Script PowerShell | Alternativa avanzada |
| `Start-Server.bat` | 📜 Script Batch | Inicia servidor + instala vJoy |
| `test_vjoy_system.py` | 🐍 Testing | Prueba el sistema |

### Documentación

| Archivo | Contenido |
|---------|----------|
| `VJOY_INSTALLER_README.md` | Guía detallada completa |
| `QUICKSTART.md` | Inicio rápido para usuarios |
| `INTEGRATION_GUIDE.md` | Guía de integración en código |
| `VJOY_INSTALLER_SYSTEM_README.md` | Este archivo |

### Sistema de Carpetas

```
python-server/
├── vJoy/                          # Carpeta de almacenamiento
│   ├── x86/                       # Instaladores 32-bit
│   │   └── vJoy_Setup.exe
│   └── x64/                       # Instaladores 64-bit
│       └── vJoy_Setup.exe
├── vjoy_installer.py              # ⭐ Descarga e instala
├── vjoy_setup_helper.py           # ⭐ Utilidades
├── vjoy_bootstrap.py              # ⭐ Integración PyQt5
├── install_vjoy.bat               # 🎯 Para usuarios
├── Install-vJoy.ps1              # 🔧 Para avanzados
├── Start-Server.bat               # 🎯 Servidor + vJoy
├── test_vjoy_system.py            # ✅ Testing
└── [Documentación .md]            # 📖 Guías
```

## 🎯 Métodos de Instalación

### Método 1: Batch Script (Recomendado para Usuarios)

```bash
# Haz doble clic en:
install_vjoy.bat
```

✅ Ventajas:
- Muy simple de usar
- Solicita confirmación del usuario
- Feedback visual
- No requiere conocimientos técnicos

### Método 2: PowerShell (Para Avanzados)

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
./Install-vJoy.ps1
```

✅ Ventajas:
- Más control
- Mejor feedback
- Soporta parámetros

### Método 3: Línea de Comandos (Para Desarrolladores)

```python
python vjoy_installer.py
```

✅ Ventajas:
- Total control
- Perfecta para automatización
- Fácil de scriptear

### Método 4: Integración en Código (Para Aplicaciones)

```python
from vjoy_setup_helper import ensure_vjoy_installed

# Al iniciar tu aplicación
ensure_vjoy_installed(ui_callback=lambda s, m: print(f"[{s}] {m}"))
```

✅ Ventajas:
- Se ejecuta automáticamente
- Transparente para el usuario
- Integración perfecta con PyQt5

## 🔄 Flujo de Instalación

```
┌─ Usuario ejecuta install_vjoy.bat
│
├─ ¿Python instalado?
│  ├─ NO → Error, instala Python
│  └─ SÍ → Continuar
│
├─ ¿vJoy instalado en el sistema?
│  ├─ SÍ → ✅ LISTO
│  └─ NO → Continuar
│
├─ ¿vJoy descargado localmente?
│  ├─ SÍ → Ir a instalación
│  └─ NO → Descargar (con progreso)
│
├─ Extraer archivos
├─ Organizar en carpetas x86/x64
│
├─ ¿Tiene permisos de admin?
│  ├─ SÍ → Instalar directamente
│  └─ NO → Solicitar elevación
│
└─ ✅ ¡COMPLETADO!
```

## 🔍 Verificación del Estado

### Verificar si vJoy está instalado

```python
from vjoy_setup_helper import VjoySetupHelper

helper = VjoySetupHelper()
status = helper.check_vjoy_status()
# Salida: 'installed', 'downloaded', o 'not_found'
```

### Ver información del sistema

```python
helper = VjoySetupHelper()
print(f"Arquitectura: {helper.get_architecture()}")      # x86 o x64
print(f"Admin: {helper.is_admin()}")                    # True/False
print(f"Ruta: {helper.get_vjoy_path()}")               # Ruta al instalador
```

### Probar desde línea de comandos

```bash
python test_vjoy_system.py
```

Esto ejecutará una verificación completa del sistema.

## 📊 API Pública

### VjoyInstaller (Bajo nivel)

```python
from vjoy_installer import VjoyInstaller

installer = VjoyInstaller()

# Métodos principales
installer.is_vjoy_installed()          # ¿Está en el sistema?
installer.vjoy_path_exists()           # ¿Está descargado?
installer.download_vjoy()              # Descargar ZIP
installer.extract_vjoy(zip_path)       # Extraer archivos
installer.install_vjoy()               # Ejecutar instalador
installer.setup_vjoy()                 # Todo el proceso
```

### VjoySetupHelper (Nivel medio)

```python
from vjoy_setup_helper import VjoySetupHelper

helper = VjoySetupHelper()

# Métodos principales
helper.check_vjoy_status()              # Estado actual
helper.needs_installation()             # ¿Necesita instalar?
helper.install_async(callbacks...)      # Instalar en async
helper.get_vjoy_path()                 # Obtener ruta
helper.get_architecture()               # x86 o x64
helper.is_admin()                      # ¿Es admin?
```

### ensure_vjoy_installed() (Alto nivel)

```python
from vjoy_setup_helper import ensure_vjoy_installed

# Función de conveniencia
ensure_vjoy_installed()

# Con callbacks
ensure_vjoy_installed(
    ui_callback=lambda status, msg: print(f"[{status}] {msg}")
)
```

### check_and_setup_vjoy() (Para PyQt5)

```python
from vjoy_bootstrap import check_and_setup_vjoy

# Verificar únicamente
if check_and_setup_vjoy(only_check=True):
    print("vJoy listo")

# Instalar con interfaz
check_and_setup_vjoy(parent_widget=self)
```

## ⚙️ Parámetros de Descarga

```python
# URL de descarga (configurable en vjoy_installer.py)
VJOY_DOWNLOAD_URL = "https://www.vjoy.org/dl/vJoy-2.2.1.1.zip"
VJOY_VERSION = "2.2.1.1"

# Para usar una versión diferente:
# Edita vjoy_installer.py y cambia VJOY_DOWNLOAD_URL
```

## 🔐 Requisitos de Permisos

| Operación | Requerimientos |
|-----------|---------------|
| Descargar ZIP | Conexión a internet |
| Extraer archivos | Permiso de escritura en carpeta |
| Instalar vJoy | Derechos de administrador |
| Usar vJoy | Aplicación con permisos suficientes |

El sistema solicitará automáticamente derechos de administrador si es necesario.

## 🐛 Solución de Problemas

### "Python no está instalado"

```
Solución: Descarga desde https://www.python.org/
Marca: "Add Python to PATH" durante la instalación
```

### "No se puede conectar a internet"

```
Solución: Verifica tu conexión WiFi/Ethernet
O: Descarga manualmente desde https://www.vjoy.org/dl/vJoy-2.2.1.1.zip
   y extrae en la carpeta vJoy/
```

### "Acceso denegado"

```
Solución: Ejecuta como Administrador
Entrada: Click derecho en install_vjoy.bat → "Ejecutar como administrador"
```

### Ver logs detallados

```python
import logging
from vjoy_installer import logger

logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Ahora ejecuta el instalador
from vjoy_installer import VjoyInstaller
installer = VjoyInstaller()
installer.setup_vjoy()
```

## 📝 Requisitos del Sistema

- **Windows 7+** (7, 8, 8.1, 10, 11)
- **Python 3.7+**
- **Conexión a Internet** (para descargar)
- **~50 MB de espacio** (para vJoy)
- **Acc acceso de administrador** (para instalar)

## 🎓 Ejemplos de Uso

### Ejemplo 1: Instalación Simple

```python
from vjoy_installer import VjoyInstaller

installer = VjoyInstaller()
success = installer.setup_vjoy()

if success:
    print("✓ vJoy instalado")
else:
    print("✗ Error en la instalación")
```

### Ejemplo 2: Con Barra de Progreso

```python
from vjoy_setup_helper import VjoySetupHelper

helper = VjoySetupHelper()

def show_progress(percent):
    print(f"Descargando: {percent}%")

def show_status(message):
    print(f"Estado: {message}")

def on_complete(success):
    print(f"¿Completado?: {success}")

helper.install_async(show_progress, show_status, on_complete)
```

### Ejemplo 3: Integración en PyQt5

```python
from vjoy_bootstrap import VjoyInstallationDialog

# En tu QMainWindow
dialog = VjoyInstallationDialog(self)
dialog.start_installation()
result = dialog.exec_()

if result:
    print("✓ vJoy listo para usar")
```

## �レソ Recursos

- **vJoy Oficial**: https://www.vjoy.org/
- **Documentación**: https://www.vjoy.org/documentation
- **pyvJoy Library**: https://github.com/tidakusno/pyvjoy
- **Forum**: https://www.vjoy.org/forum

## 🔄 Actualización

Para actualizar vJoy:

1. Elimina la carpeta `vJoy/` completamente
2. Ejecuta `install_vjoy.bat` nuevamente
3. Se descargará la versión configurada

Para cambiar la versión:

1. Edita `vjoy_installer.py`
2. Cambia `VJOY_DOWNLOAD_URL` a la nueva versión
3. Cambia `VJOY_VERSION` al número de versión
4. Guarda y ejecuta el instalador

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Archivos Python | 3 |
| Scripts Batch/PS | 3 |
| Documentación | 4 MD |
| Líneas de código | ~1,500 |
| Funcionalidades | 25+ |
| Arquitecturas soportadas | 2 (x86, x64) |

## ✅ Checklist de Verificación

- ✅ Descarga automática de vJoy
- ✅ Extracción automática de archivos
- ✅ Organización por arquitectura (x86/x64)
- ✅ Detección automática de sistema
- ✅ Solicitud de permisos de admin
- ✅ Instalación silenciosa
- ✅ Barras de progreso
- ✅ Manejo de errores
- ✅ Integración con PyQt5
- ✅ API simple y clara
- ✅ Documentación completa
- ✅ Scripts ejecutables
- ✅ Testing incluido
- ✅ Logging detallado

## 🎁 Bonus Features

- Descarga caché (no descarga si ya está)
- Validación de arquitectura automática
- Permisos de admin automáticos
- Interfaz de instalación visual (PyQt5)
- APIs múltiples (bajo nivel a alto nivel)
- Documentación completa en español

## 📞 Soporte

Para problemas o sugerencias:
1. Consulta [VJOY_INSTALLER_README.md](VJOY_INSTALLER_README.md)
2. Ejecuta `test_vjoy_system.py` para diagnóstico
3. Revisa los logs en consola
4. Visita https://www.vjoy.org/

## 📄 Licencia

Este instalador es de código abierto y puede ser distribuido libremente con tu aplicación.

vJoy es gratuito bajo su licencia específica. Consulta https://www.vjoy.org/ para detalles.

---

** 🚀 ¡Listo para usar! Ejecuta `install_vjoy.bat` o `Start-Server.bat` ahora.**
