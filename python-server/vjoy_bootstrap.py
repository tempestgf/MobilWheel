"""
vJoy Auto-Bootstrap Module
Integración automática de verificación e instalación de vJoy en aplicaciones PyQt5
"""

import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QPushButton, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QTextCursor

from vjoy_setup_helper import VjoySetupHelper

class VjoyInstallationSignals(QObject):
    """Señales para la instalación de vJoy"""
    progress = pyqtSignal(int)
    status_changed = pyqtSignal(str)
    completed = pyqtSignal(bool)
    log_message = pyqtSignal(str)


class VjoyInstallationDialog(QDialog):
    """Diálogo de instalación de vJoy para PyQt5"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.helper = VjoySetupHelper()
        self.signals = VjoyInstallationSignals()
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        self.setWindowTitle("Instalador de vJoy")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Instalando vJoy")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Descripción
        description = QLabel(
            "Se está descargando e instalando vJoy (driver virtual de controles).\n"
            "Este proceso puede tomar unos minutos..."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #00ff00; font-family: Courier; }")
        layout.addWidget(self.log_text)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.cancel_installation)
        buttons_layout.addWidget(self.cancel_button)
        
        self.manual_button = QPushButton("Instalar vJoy manualmente")
        self.manual_button.clicked.connect(self.open_manual_download)
        self.manual_button.setVisible(False)
        buttons_layout.addWidget(self.manual_button)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Conectar señales
        self.signals.progress.connect(self.on_progress)
        self.signals.status_changed.connect(self.on_status_changed)
        self.signals.log_message.connect(self.on_log_message)
        self.signals.completed.connect(self.on_completed)
    
    def start_installation(self):
        """Inicia la instalación de vJoy"""
        def on_progress(percent):
            self.signals.progress.emit(percent)
        
        def on_install_status(message):
            self.signals.status_changed.emit(message)
        
        def on_complete(success):
            self.signals.completed.emit(success)
        
        # Iniciar instalación en thread
        self.helper.install_async(
            on_progress=on_progress,
            on_install_status=on_install_status,
            on_complete=on_complete
        )
    
    def on_progress(self, percent):
        """Actualizar barra de progreso"""
        self.progress_bar.setValue(percent)
    
    def on_status_changed(self, status):
        """Actualizar estado"""
        self.log_text.append(f"➜ {status}")
        # Auto-scroll
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def on_log_message(self, message):
        """Agregar mensaje de log"""
        self.log_text.append(message)
    
    def on_completed(self, success):
        """Cuando finaliza la instalación"""
        self.cancel_button.setText("Cerrar")
        if success:
            self.log_text.append("✓ ¡Instalación completada!")
        else:
            self.log_text.append("✗ La instalación falló (Vjoy)")
            self.manual_button.setVisible(True)

    def open_manual_download(self):
        import webbrowser
        webbrowser.open('https://www.vjoy.org/es/download-for-windows')
    
    def cancel_installation(self):
        """Cancelar o cerrar"""
        self.close()


def check_and_setup_vjoy(parent_widget=None, only_check=False):
    """
    Verifica el estado de vJoy y lo instala si es necesario
    
    Args:
        parent_widget: Widget padre para el diálogo
        only_check: Si es True, solo verifica sin instalar
    
    Returns:
        bool: True si vJoy está disponible, False en caso contrario
    """
    if sys.platform != 'win32':
        return True
        
    helper = VjoySetupHelper()
    status = helper.check_vjoy_status()
    
    if status == 'installed':
        return True
    
    if only_check:
        return False
    
    # Mostrar diálogo de instalación
    if parent_widget:
        dialog = VjoyInstallationDialog(parent_widget)
        dialog.start_installation()
        dialog.exec_()
        
        # Verificar si fue exitoso
        return helper.check_vjoy_status() == 'installed'
    else:
        # Instalación sin interfaz gráfica
        def status_callback(status, message):
            print(f"[{status}] {message}")
        
        from vjoy_setup_helper import ensure_vjoy_installed
        ensure_vjoy_installed(ui_callback=status_callback)
        
        return helper.check_vjoy_status() == 'installed'


# Código de integración automática para ServerApp.py
VJOY_BOOTSTRAP_CODE = '''
# ═══════════════════════════════════════════════════════════════════════════════
# vJoy Auto-Bootstrap - Agregar esto al __init__ del ServerApp
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from vjoy_bootstrap import check_and_setup_vjoy
    
    # Verificar vJoy al iniciar
    if not check_and_setup_vjoy(parent_widget=self, only_check=True):
        logging.warning("vJoy no está instalado, iniciando instalación...")
        check_and_setup_vjoy(parent_widget=self)
except ImportError:
    logging.warning("vjoy_bootstrap no disponible")
except Exception as e:
    logging.error(f"Error verificando vJoy: {e}")
'''


if __name__ == "__main__":
    # Para pruebas de la interfaz
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = VjoyInstallationDialog()
    dialog.show()
    dialog.start_installation()
    
    sys.exit(app.exec_())
