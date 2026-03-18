"""
vJoy Setup Helper - Facilita la instalación de vJoy con interfaz gráfica
"""

import os
import sys
import threading
from pathlib import Path
from vjoy_installer import VjoyInstaller

class VjoySetupHelper:
    """Helper para integrar la instalación de vJoy con la UI"""
    
    def __init__(self):
        self.installer = VjoyInstaller()
        self.installation_complete = False
        self.installation_success = False
        
    def check_vjoy_status(self):
        """
        Retorna el estado de vJoy:
        - 'installed': Ya está instalado en el sistema
        - 'downloaded': Descargado pero no instalado
        - 'not_found': No está disponible
        """
        if self.installer.is_vjoy_installed():
            return 'installed'
        elif self.installer.vjoy_path_exists():
            return 'downloaded'
        else:
            return 'not_found'
    
    def needs_installation(self):
        """Determina si necesita instalar vJoy"""
        return self.check_vjoy_status() != 'installed'
    
    def install_async(self, on_progress=None, on_install_status=None, on_complete=None):
        """
        Instala vJoy de forma asíncrona en un thread separado
        
        Args:
            on_progress: callback(percent) - Progreso de descarga 0-100
            on_install_status: callback(message) - Estado de instalación
            on_complete: callback(success) - Se llama cuando finaliza
        """
        def install_thread():
            try:
                self.installation_success = self.installer.setup_vjoy(
                    progress_callback=on_progress,
                    install_callback=on_install_status
                )
            except Exception as e:
                print(f"Error en instalación: {e}")
                self.installation_success = False
            finally:
                self.installation_complete = True
                if on_complete:
                    on_complete(self.installation_success)
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
        return thread
    
    def get_vjoy_path(self):
        """Retorna la ruta del instalador de vJoy si está descargado"""
        if self.installer.vjoy_path_exists():
            return str(self.installer.installed_path)
        return None
    
    def get_architecture(self):
        """Retorna la arquitectura detectada (x86 o x64)"""
        return self.installer.architecture
    
    @staticmethod
    def is_admin():
        """Verifica si se están ejecutando con derechos de administrador"""
        try:
            import ctypes
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False

# Función de conveniencia para integración rápida
def ensure_vjoy_installed(ui_callback=None):
    """
    Asegura que vJoy esté instalado, con feedback opcional en la UI
    
    Args:
        ui_callback: callable(status, message) para actualizar la UI
    
    Returns:
        bool: True si está instalado, False en caso contrario
    """
    helper = VjoySetupHelper()
    status = helper.check_vjoy_status()
    
    if status == 'installed':
        if ui_callback:
            ui_callback('success', '✓ vJoy está correctamente instalado')
        return True
    
    if ui_callback:
        ui_callback('info', 'Preparando vJoy...')
    
    def on_progress(percent):
        if ui_callback:
            ui_callback('progress', f'Descargando... {percent}%')
    
    def on_install_status(message):
        if ui_callback:
            ui_callback('info', message)
    
    def on_complete(success):
        if ui_callback:
            if success:
                ui_callback('success', '✓ vJoy instalado correctamente')
            else:
                ui_callback('error', '✗ No se pudo instalar vJoy automáticamente')
    
    helper.install_async(on_progress, on_install_status, on_complete)
    return False  # Aún se está descargando/instalando
