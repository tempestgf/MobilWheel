# 🔌 Guía de Integración - vJoy en ServerApp

Esta guía explain cómo integrar el sistema automático de instalación de vJoy en tu aplicación PyQt5.

## Opción 1: Integración Automática (Recomendada)

### Paso 1: Agregar importación en ServerApp.py

En la sección de imports al inicio de `ServerApp.py`, agrega:

```python
try:
    from vjoy_bootstrap import check_and_setup_vjoy
    HAS_VJOY_BOOTSTRAP = True
except ImportError:
    HAS_VJOY_BOOTSTRAP = False
    logging.warning("vjoy_bootstrap module not available")
```

### Paso 2: Agregar verificación en __init__

En el método `__init__` de la clase `ServerApp`, después de que se haya creado la interfaz gráfica, agrega:

```python
class ServerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... Tu código existente ...
        
        # Verificar e instalar vJoy si es necesario
        if HAS_VJOY_BOOTSTRAP:
            self.setup_vjoy_async()
    
    def setup_vjoy_async(self):
        """Configurar vJoy en segundo plano"""
        from vjoy_setup_helper import VjoySetupHelper
        
        helper = VjoySetupHelper()
        status = helper.check_vjoy_status()
        
        if status == 'installed':
            self.log_message("✓ vJoy está correctamente instalado")
        elif status == 'downloaded':
            self.log_message("⚙️ vJoy descargado, iniciando instalación...")
            self.start_vjoy_installation()
        else:
            self.log_message("📥 Descargando vJoy...")
            self.start_vjoy_installation()
    
    def start_vjoy_installation(self):
        """Inicia la instalación de vJoy"""
        from vjoy_bootstrap import VjoyInstallationDialog
        
        dialog = VjoyInstallationDialog(self)
        dialog.start_installation()
        dialog.exec_()
        
        # Verificar si fue exitoso
        from vjoy_setup_helper import VjoySetupHelper
        if VjoySetupHelper().check_vjoy_status() == 'installed':
            self.log_message("✓ vJoy instalado correctamente")
        else:
            self.log_message("✗ Error instalando vJoy")
```

### Paso 3: Agregar método de logging

Si aún no lo tienes, asegúrate de tener un método `log_message`:

```python
def log_message(self, message):
    """Agrega un mensaje al log"""
    timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
    self.log_text.append(f"[{timestamp}] {message}")
```

## Opción 2: Verificación Manual

Si prefieres una integración más simple sin UI de instalación:

```python
from vjoy_setup_helper import VjoySetupHelper

def check_vjoy():
    helper = VjoySetupHelper()
    
    if helper.is_vjoy_installed():
        print("✓ vJoy instalado")
        return True
    else:
        print("✗ vJoy no está instalado")
        print(f"  Ejecuta: {Path(__file__).parent / 'install_vjoy.bat'}")
        return False

# En tu __init__:
if not check_vjoy():
    logging.warning("vJoy no está disponible")
```

## Opción 3: Instalación Silenciosa en Background

Para instalar sin mostrar una interfaz:

```python
from vjoy_setup_helper import ensure_vjoy_installed

def setup_vjoy_background(self):
    """Configura vJoy en background sin bloquear la UI"""
    def status_update(status, message):
        self.log_message(f"[{status}] {message}")
    
    ensure_vjoy_installed(ui_callback=status_update)
```

## Estructura del Archivo ServerApp.py (Ejemplo Completo)

```python
import os
import sys
import threading
import logging
from io import StringIO
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QTextEdit, QPushButton)
from PyQt5.QtCore import QDateTime

# ═════════════════════════════════════════════════════════════════
# 1. IMPORTAR VJOY BOOTSTRAP
# ═════════════════════════════════════════════════════════════════
try:
    from vjoy_bootstrap import check_and_setup_vjoy
    HAS_VJOY = True
except ImportError:
    HAS_VJOY = False
    logging.warning("vJoy bootstrap not available")


# ═════════════════════════════════════════════════════════════════
# 2. CONFIGURACIÓN DE LOGGING
# ═════════════════════════════════════════════════════════════════
log_stream = StringIO()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=log_stream
)


# ═════════════════════════════════════════════════════════════════
# 3. CLASE PRINCIPAL
# ═════════════════════════════════════════════════════════════════
class ServerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobile Wheel Server")
        
        # UI principal
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Label
        self.label = QLabel("Iniciando servidor...")
        layout.addWidget(self.label)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Botón
        button = QPushButton("Iniciar Servidor")
        button.clicked.connect(self.start_server)
        layout.addWidget(button)
        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        # ═════════════════════════════════════════════════════════
        # 4. INICIALIZAR VJOY
        # ═════════════════════════════════════════════════════════
        if HAS_VJOY:
            self.log_message("Verificando vJoy...")
            self.setup_vjoy()
    
    def log_message(self, message):
        """Agrega mensaje al log"""
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.log_text.append(f"[{timestamp}] {message}")
    
    def setup_vjoy(self):
        """Configurar vJoy"""
        from vjoy_setup_helper import VjoySetupHelper
        
        helper = VjoySetupHelper()
        status = helper.check_vjoy_status()
        
        if status == 'installed':
            self.log_message("✓ vJoy está disponible")
            return
        
        # Si no está instalado, mostrar diálogo
        from vjoy_bootstrap import VjoyInstallationDialog
        
        dialog = VjoyInstallationDialog(self)
        dialog.start_installation()
        
        # Ejecutar no-bloqueante
        def run_dialog():
            dialog.exec_()
        
        thread = threading.Thread(target=run_dialog, daemon=True)
        thread.start()
    
    def start_server(self):
        """Iniciar servidor"""
        self.log_message("Iniciando servidor...")
        # Tu código de servidor aquí
        pass


# ═════════════════════════════════════════════════════════════════
# 5. PUNTO DE ENTRADA
# ═════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerApp()
    window.show()
    sys.exit(app.exec_())
```

## API de vjoy_setup_helper

### VjoySetupHelper()

```python
from vjoy_setup_helper import VjoySetupHelper

helper = VjoySetupHelper()

# Verificar estado
status = helper.check_vjoy_status()
# Retorna: 'installed', 'downloaded', o 'not_found'

# ¿Necesita instalación?
if helper.needs_installation():
    print("Necesita instalar vJoy")

# Obtener arquitectura
arch = helper.get_architecture()  # 'x86' o 'x64'

# Obtener ruta del instalador
path = helper.get_vjoy_path()  # Ruta completa o None

# Verificar derechos de administrador
if helper.is_admin():
    print("Ejecutando como administrador")

# Instalar de forma asíncrona
def on_progress(percent):
    print(f"Descargando... {percent}%")

def on_status(message):
    print(f"Estado: {message}")

def on_complete(success):
    print(f"¿Exitoso? {success}")

helper.install_async(on_progress, on_status, on_complete)
```

### ensure_vjoy_installed()

```python
from vjoy_setup_helper import ensure_vjoy_installed

# Uso simple
ensure_vjoy_installed()

# Con callbacks
def callback(status, message):
    print(f"[{status}] {message}")

ensure_vjoy_installed(ui_callback=callback)
```

## Manejo de Errores

```python
from vjoy_setup_helper import VjoySetupHelper

try:
    helper = VjoySetupHelper()
    helper.setup_vjoy()
except PermissionError:
    logging.error("Se requieren derechos de administrador")
except Exception as e:
    logging.error(f"Error con vJoy: {e}")
```

## Testing

Para probar la integración:

```python
# test_vjoy_integration.py
from vjoy_setup_helper import VjoySetupHelper

def test_vjoy():
    helper = VjoySetupHelper()
    
    print(f"Status: {helper.check_vjoy_status()}")
    print(f"Architecture: {helper.get_architecture()}")
    print(f"Admin: {helper.is_admin()}")
    print(f"Needs installation: {helper.needs_installation()}")

if __name__ == "__main__":
    test_vjoy()
```

Ejecutar con:
```cmd
python test_vjoy_integration.py
```

## Envío a Usuarios

Cuando envíes tu aplicación a usuarios, SOLO necesitas incluir:

```
ServerApp.py (actualizado)
vjoy_bootstrap.py
vjoy_setup_helper.py
vjoy_installer.py
install_vjoy.bat
Install-vJoy.ps1
VJOY_INSTALLER_README.md
QUICKSTART.md
vJoy/
  ├── x86/
  └── x64/
```

Los usuarios solo necesitan ejecutar `install_vjoy.bat` o `Start-Server.bat`.

## Troubleshooting de Integración

| Problema | Solución |
|----------|----------|
| "ImportError: No module named vjoy_bootstrap" | Asegúrate que el archivo está en la misma carpeta que ServerApp.py |
| Dialog no aparece | Verifica que estés pasando `self` como parent |
| No se descarga | Verifica conexión a internet y que el URL es válido |

---

¡Listo! Tu aplicación ahora tiene soporte automático para la instalación de vJoy.
