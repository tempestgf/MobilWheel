"""
vJoy Installer - Descarga e instala vJoy automáticamente
Soporta arquitecturas x86 y x64

Versión: 1.0.0
Producción: Sí
Compatibilidad: Windows 7+, Python 3.7+
"""

import os
import sys
import urllib.request
import urllib.error
import zipfile
import subprocess
import platform
import logging
from pathlib import Path
import ctypes
import socket
from typing import Optional, Callable

# Configurar logging con formato estructurado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constantes
VJOY_DOWNLOAD_URL = "https://www.vjoy.org/dl/vJoy-2.2.1.1.zip"
VJOY_VERSION = "2.2.1.1"
VJOY_FOLDER = Path(__file__).parent / "vJoy"
DOWNLOAD_TIMEOUT = 300  # 5 minutos
CONNECTION_TIMEOUT = 10  # 10 segundos
RETRY_ATTEMPTS = 3

# Excepciones personalizadas
class VjoyException(Exception):
    """Excepción base para vJoy"""
    pass

class VjoyDownloadError(VjoyException):
    """Error durante la descarga"""
    pass

class VjoyInstallationError(VjoyException):
    """Error durante la instalación"""
    pass

class VjoyPermissionError(VjoyException):
    """Error de permisos"""
    pass

class VjoyInstaller:
    """Gestor de descargas e instalación de vJoy"""
    
    def __init__(self):
        self.vjoy_folder = VJOY_FOLDER
        self.vjoy_folder.mkdir(exist_ok=True)
        self.architecture = self._detect_architecture()
        self.installed_path = None
        
    def _detect_architecture(self):
        """Detecta si el sistema es x86 o x64"""
        if sys.maxsize > 2**32:
            return "x64"
        else:
            return "x86"
    
    def _get_admin_rights(self):
        """Verifica si se tienen derechos de administrador"""
        try:
            return ctypes.windll.shell.IsUserAnAdmin()
        except:
            return False
    
    def is_vjoy_installed(self):
        """Verifica si vJoy está instalado en el sistema"""
        # Primero revisamos si el driver y la DLL de vJoy existen en las rutas de Windows
        import os
        vjoy_paths = [
            r"C:\Program Files\vJoy\x64\vJoyInterface.dll",
            r"C:\Program Files\vJoy\x86\vJoyInterface.dll",
            r"C:\Program Files (x86)\vJoy\x86\vJoyInterface.dll"
        ]
        
        driver_found = any(os.path.exists(p) for p in vjoy_paths)
        if driver_found:
            logger.info("✓ El driver de vJoy está instalado en el sistema")
            return True
            
        try:
            # Intenta importar pyvjoy como alternativa
            import pyvjoy
            logger.info("✓ pyvJoy está disponible")
            return True
        except ImportError:
            logger.info("✗ pyvJoy no está instalado y no se encontró el driver vJoy")
            return False
    
    def vjoy_path_exists(self):
        """Verifica si vJoy está descargado localmente"""
        # Buscar el instalador unificado primero en vjoy_folder
        exe_files = list(self.vjoy_folder.glob("*.exe"))
        if exe_files:
            self.installed_path = exe_files[0]
            logger.info(f"✓ vJoy encontrado en: {self.installed_path}")
            return True
            
        arch_folder = self.vjoy_folder / self.architecture
        if arch_folder.exists():
            exe_files = list(arch_folder.glob("*.exe"))
            if exe_files:
                self.installed_path = exe_files[0]
                logger.info(f"✓ vJoy encontrado en: {self.installed_path}")
                return True
        return False
    
    def download_vjoy(self, progress_callback: Optional[Callable] = None) -> Path:
        """
        Descarga vJoy desde el sitio oficial con reintentos
        
        Args:
            progress_callback: Función para reportar progreso (percent: 0-100)
        
        Returns:
            Ruta del archivo descargado
        
        Raises:
            VjoyDownloadError: Si la descarga falla después de reintentos
        """
        logger.info(f"📥 Descargando vJoy {VJOY_VERSION}...")
        
        zip_path = self.vjoy_folder / f"vJoy-{VJOY_VERSION}.zip"
        
        # Limpiar descarga anterior si existe
        if zip_path.exists():
            try:
                zip_path.unlink()
                logger.debug(f"Archivo anterior eliminado: {zip_path}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar archivo anterior: {e}")
        
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                logger.debug(f"Intento de descarga {attempt}/{RETRY_ATTEMPTS}")

                # Opción 1: Powerhsell (fiable en Windows)
                ps_command = f"Invoke-WebRequest -Uri '{VJOY_DOWNLOAD_URL}' -OutFile '{zip_path}' -UseBasicParsing"
                try:
                    subprocess.run(["powershell", "-Command", ps_command], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if zip_path.exists() and zip_path.stat().st_size > 1000000:
                        file_size = zip_path.stat().st_size
                        logger.info(f"✓ Descarga completada via PowerShell ({file_size / 1024 / 1024:.1f} MB)")
                        if progress_callback:
                            progress_callback(100)
                        return zip_path
                except Exception as ps_exc:
                    logger.warning(f"PowerShell download falló, usando urllib: {ps_exc}")

                # Opción 2: urllib con opener (por si no funciona powershell)
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mobile-Wheel-Server/1.0')]
                urllib.request.install_opener(opener)

                with urllib.request.urlopen(VJOY_DOWNLOAD_URL) as response, open(zip_path, 'wb') as out_file:
                    total_size = int(response.getheader('Content-Length', 0))
                    block_size = max(4096, total_size // 100) if total_size else 8192
                    downloaded = 0
                    
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        out_file.write(buffer)
                        
                        if progress_callback and total_size > 0:
                            percent = min(100, int(downloaded * 100 / total_size))
                            progress_callback(percent)
                
                # Validar que el archivo se descargó
                if not zip_path.exists():
                    raise VjoyDownloadError("Archivo no se creó después de descarga")
                
                file_size = zip_path.stat().st_size
                if file_size < 1024 * 1024:  # Menos de 1MB es sospechoso
                    logger.warning(f"Tamaño de descarga sospechoso: {file_size} bytes")
                
                logger.info(f"✓ Descarga completada ({file_size / 1024 / 1024:.1f} MB)")
                socket.setdefaulttimeout(None)
                return zip_path
                
            except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout) as e:
                logger.warning(f"Error de conexión en intento {attempt}: {e}")
                if attempt < RETRY_ATTEMPTS:
                    logger.info(f"Reintentando en 5 segundos...")
                    import time
                    time.sleep(5)
                else:
                    raise VjoyDownloadError(f"No se pudo descargar vJoy después de {RETRY_ATTEMPTS} intentos: {e}")
            
            except Exception as e:
                import traceback
                logger.error(f"Error inesperado en descarga: {e}\n{traceback.format_exc()}")
                raise VjoyDownloadError(f"Error descargando vJoy: {e}")
            
            finally:
                socket.setdefaulttimeout(None)
    
    def extract_vjoy(self, zip_path: Path) -> bool:
        """
        Extrae el archivo ZIP de vJoy
        
        Args:
            zip_path: Ruta del archivo ZIP
        
        Returns:
            True si la extracción fue exitosa
        
        Raises:
            VjoyException: Si la extracción falla
        """
        logger.info("📦 Extrayendo archivos...")
        
        if not zip_path.exists():
            raise VjoyException(f"Archivo ZIP no encontrado: {zip_path}")
        
        try:
            # Validar integridad del ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Verificar que el ZIP es válido
                bad_file = zip_ref.testzip()
                if bad_file:
                    raise VjoyException(f"ZIP corrompido. Archivo problemático: {bad_file}")
                
                # Extraer archivos
                zip_ref.extractall(self.vjoy_folder)
            
            logger.info("✓ Extracción completada")
            
            # Reorganizar archivos si es necesario
            self._organize_vjoy_files()
            
            # Limpiar ZIP exitosamente
            try:
                zip_path.unlink()
                logger.debug(f"Archivo ZIP eliminado: {zip_path}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar ZIP: {e}")
            
            return True
            
        except zipfile.BadZipFile:
            raise VjoyException(f"ZIP corrompido o inválido: {zip_path}")
        except Exception as e:
            logger.error(f"✗ Error extrayendo vJoy: {e}")
            raise VjoyException(f"Error extrayendo archivos: {e}")
    
    def _organize_vjoy_files(self):
        """Organiza los archivos descargados en carpetas x86/x64"""
        logger.info("📁 Organizando archivos...")
        
        # Buscar carpetas vJoy en el directorio
        for item in self.vjoy_folder.iterdir():
            if item.is_dir() and "vJoy" in item.name:
                # Buscar instaladores en esta carpeta
                for exe in item.glob("**/*.exe"):
                    if "x64" in str(exe).upper() or "64" in str(exe):
                        target_dir = self.vjoy_folder / "x64"
                        target_dir.mkdir(exist_ok=True)
                        target_file = target_dir / exe.name
                        if not target_file.exists():
                            exe.rename(target_file)
                            logger.info(f"  ✓ Movido: {exe.name} → x64/")
                    
                    elif "x86" in str(exe).upper() or "32" in str(exe):
                        target_dir = self.vjoy_folder / "x86"
                        target_dir.mkdir(exist_ok=True)
                        target_file = target_dir / exe.name
                        if not target_file.exists():
                            exe.rename(target_file)
                            logger.info(f"  ✓ Movido: {exe.name} → x86/")
    
    def install_vjoy(self):
        """Instala vJoy ejecutando el instalador"""
        if not self.vjoy_path_exists():
            logger.error("✗ No se encontró el instalador de vJoy")
            return False
        
        logger.info(f"⚙️  Instalando vJoy desde {self.installed_path}...")
        
        if not self._get_admin_rights():
            logger.warning("⚠️  Se requieren derechos de administrador para instalar vJoy")
            logger.info("   Reiniciando con privilegios elevados...")
            
            # Re-ejecutar con derechos de administrador
            try:
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    str(self.installed_path),
                    "/S",  # Instalación silenciosa
                    None,
                    1
                )
                if result <= 32:
                    raise Exception(f"ShellExecuteW failed with code {result}")
                logger.info("✓ Instalador iniciado con privilegios de administrador")
                return True
            except Exception as e:
                logger.error(f"✗ Error elevando privilegios: {e}")
                logger.info("   Por favor, ejecute manualmente: " + str(self.installed_path))
                return False
        else:
            try:
                # Ejecutar instalador silencioso
                subprocess.run([str(self.installed_path), '/S'], check=True)
                logger.info("✓ vJoy instalado correctamente")
                return True
            except Exception as e:
                logger.error(f"✗ Error durante la instalación: {e}")
                return False
    
    def setup_vjoy(self, progress_callback: Optional[Callable] = None, 
                   install_callback: Optional[Callable] = None) -> bool:
        """
        Flujo completo: verificar, descargar, instalar
        
        Args:
            progress_callback: Función para reportar progreso (percent: 0-100)
            install_callback: Función para reportar estado de instalación
        
        Returns:
            True si la instalación fue exitosa, False en caso contrario
        """
        logger.info("=" * 70)
        logger.info("INICIANDO INSTALACIÓN DE VJOY")
        logger.info(f"Versión: {VJOY_VERSION} | Arquitectura: {self.architecture}")
        logger.info("=" * 70)
        
        try:
            # Paso 1: Verificar si ya está instalado
            logger.info("Paso 1: Verificando si vJoy ya está instalado...")
            if self.is_vjoy_installed():
                logger.info("✓ vJoy ya está instalado en el sistema")
                return True
            
            # Paso 2: Verificar si está descargado
            logger.info("Paso 2: Verificando descarga local...")
            if not self.vjoy_path_exists():
                logger.info(f"Detectado: Arquitectura {self.architecture}")
                logger.info("Paso 3: Descargando vJoy...")
                
                try:
                    zip_path = self.download_vjoy(progress_callback)
                    logger.info("Paso 4: Extrayendo archivos...")
                    self.extract_vjoy(zip_path)
                except VjoyDownloadError as e:
                    logger.error(f"✗ Error en descarga: {e}")
                    return False
                except Exception as e:
                    logger.error(f"✗ Error inesperado en descarga: {e}")
                    return False
            else:
                logger.info("✓ vJoy ya está descargado localmente")
            
            # Paso 5: Instalar
            logger.info("Paso 5: Instalando vJoy...")
            if self.vjoy_path_exists():
                if install_callback:
                    install_callback(f"Instalando vJoy desde {self.installed_path}")
                
                try:
                    success = self.install_vjoy()
                    logger.info("=" * 70)
                    return success
                except (VjoyInstallationError, VjoyPermissionError) as e:
                    logger.error(f"✗ Error en instalación: {e}")
                    return False
            
            logger.error("✗ vJoy no se encontró después de descarga")
            return False
            
        except Exception as e:
            logger.exception(f"✗ Error fatal inesperado: {e}")
            return False

def main():
    """Función principal para ejecutar desde línea de comandos"""
    installer = VjoyInstaller()
    
    try:
        success = installer.setup_vjoy()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
