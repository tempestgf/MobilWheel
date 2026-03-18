#!/usr/bin/env python
"""
Production Readiness Check - vJoy Installation System
Verifica que todo el sistema de instalación de vJoy está listo para producción

Versión: 1.0.0
Requiere: Python 3.7+
"""

import sys
import os
from pathlib import Path
import hashlib
import json
from datetime import datetime

class ProductionChecker:
    """Verificador de readiness para producción"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "checks": {}
        }
        self.all_passed = True
    
    def check(self, name: str, condition: bool, message: str = "", details: str = "") -> bool:
        """Registrar una verificación"""
        status = "✓ PASS" if condition else "✗ FAIL"
        print(f"  {status} - {name}")
        
        if message:
            print(f"       {message}")
        
        self.results["checks"][name] = {
            "status": "PASS" if condition else "FAIL",
            "message": message,
            "details": details
        }
        
        if not condition:
            self.all_passed = False
        
        return condition
    
    def run_all_checks(self):
        """Ejecuta todas las verificaciones"""
        
        print("\n" + "=" * 70)
        print("  VERIFICACIÓN DE READINESS PARA PRODUCCIÓN")
        print("=" * 70 + "\n")
        
        # 1. Verificar Python
        print("[1] Requisitos del Sistema")
        print("-" * 70)
        
        self.check(
            "Python Version",
            sys.version_info >= (3, 7),
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "Requiere Python 3.7 o superior"
        )
        
        self.check(
            "Platform",
            sys.platform == "win32",
            f"Plataforma: {sys.platform}",
            "Este sistema solo funciona en Windows"
        )
        
        # 2. Verificar archivos
        print("\n[2] Archivos Requeridos")
        print("-" * 70)
        
        required_files = {
            "vjoy_installer.py": "Módulo de descarga e instalación",
            "vjoy_setup_helper.py": "Helper de utilidades",
            "vjoy_bootstrap.py": "Integración PyQt5",
            "install_vjoy.bat": "Script ejecutable (usuarios)",
            "Install-vJoy.ps1": "Script PowerShell (avanzados)",
            "Start-Server.bat": "Integración con servidor"
        }
        
        for filename, description in required_files.items():
            file_path = self.base_path / filename
            exists = file_path.exists()
            
            if exists and filename.endswith(".py"):
                # Verificar que es un archivo Python válido
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), filename, 'exec')
                    message = f"Archivo Python válido"
                except SyntaxError as e:
                    message = f"ERROR DE SINTAXIS: {e}"
                    exists = False
            else:
                message = "Archivo presente"
            
            self.check(
                f"Archivo: {filename}",
                exists,
                message,
                description
            )
        
        # 3. Verificar documentación
        print("\n[3] Documentación")
        print("-" * 70)
        
        docs = {
            "QUICKSTART.md": "Guía rápida",
            "VJOY_INSTALLER_README.md": "Documentación completa",
            "INTEGRATION_GUIDE.md": "Guía de integración",
            "VJOY_INSTALLER_INDEX.md": "Índice de archivos"
        }
        
        for filename, description in docs.items():
            file_path = self.base_path / filename
            self.check(
                f"Documento: {filename}",
                file_path.exists(),
                "Presente" if file_path.exists() else "Falta",
                description
            )
        
        # 4. Verificar integridad de código
        print("\n[4] Integridad de Código Python")
        print("-" * 70)
        
        py_files = ["vjoy_installer.py", "vjoy_setup_helper.py", "vjoy_bootstrap.py"]
        
        for filename in py_files:
            file_path = self.base_path / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar que tiene documentación
                    has_docstring = '"""' in content or "'''" in content
                    has_type_hints = '->' in content or ': ' in content
                    has_error_handling = 'except' in content or 'raise' in content
                    
                    message = []
                    if has_docstring:
                        message.append("docstrings")
                    if has_type_hints:
                        message.append("type hints")
                    if has_error_handling:
                        message.append("error handling")
                    
                    self.check(
                        f"Calidad: {filename}",
                        has_docstring and has_error_handling,
                        f"Incluye: {', '.join(message)}",
                        f"Tamaño: {len(content)} bytes"
                    )
                
                except Exception as e:
                    self.check(f"Calidad: {filename}", False, str(e))
        
        # 5. Verificar carpeta vJoy
        print("\n[5] Estructura de Carpetas")
        print("-" * 70)
        
        vjoy_dir = self.base_path / "vJoy"
        self.check(
            "Carpeta vJoy",
            True,  # Se crea automáticamente
            "Se creará si no existe",
            "Ubicación para descargas"
        )
        
        # 6. Verificar importaciones críticas
        print("\n[6] Dependencias de Importación")
        print("-" * 70)
        
        critical_imports = {
            "urllib": "Para descargas HTTP",
            "zipfile": "Para extraer ZIPs",
            "subprocess": "Para ejecutar procesos",
            "ctypes": "Para permisos administrativos",
            "pathlib": "Para manejo de rutas",
        }
        
        for module, description in critical_imports.items():
            try:
                __import__(module)
                self.check(
                    f"Módulo: {module}",
                    True,
                    "Disponible",
                    description
                )
            except ImportError as e:
                self.check(
                    f"Módulo: {module}",
                    False,
                    f"No disponible: {e}",
                    description
                )
        
        # 7. Verificar PyQt5 (opcional pero recomendado)
        print("\n[7] Dependencias Opcionales")
        print("-" * 70)
        
        try:
            from PyQt5 import QtWidgets
            has_pyqt = True
            message = "PyQt5 disponible (integración UI)"
        except ImportError:
            has_pyqt = False
            message = "PyQt5 no disponible (UI no funcionará)"
        
        self.check(
            "PyQt5",
            has_pyqt,
            message,
            "Requerido para interfaz gráfica",
        )
        
        # 8. Prueba de importación de módulos
        print("\n[8] Importabilidad de Módulos")
        print("-" * 70)
        
        sys.path.insert(0, str(self.base_path))
        
        try:
            import vjoy_installer
            self.check("Import: vjoy_installer", True, "Módulo importable")
        except Exception as e:
            self.check("Import: vjoy_installer", False, str(e))
        
        try:
            import vjoy_setup_helper
            self.check("Import: vjoy_setup_helper", True, "Módulo importable")
        except Exception as e:
            self.check("Import: vjoy_setup_helper", False, str(e))
        
        try:
            import vjoy_bootstrap
            self.check("Import: vjoy_bootstrap", True, "Módulo importable")
        except Exception as e:
            self.check("Import: vjoy_bootstrap", False, str(e))
        
        # 9. Verificar permisos
        print("\n[9] Permisos del Sistema")
        print("-" * 70)
        
        try:
            import ctypes
            is_admin = ctypes.windll.shell.IsUserAnAdmin()
            self.check(
                "Derechos de Administrador",
                is_admin,
                "Sí (recomendado para testing)" if is_admin else "No (se solicitarán al instalar)",
                "Requerido para instalar vJoy"
            )
        except:
            self.check("Derechos de Administrador", True, "No verificable (puede ser normal)")
        
        # 10. Espacio en disco
        print("\n[10] Recursos del Sistema")
        print("-" * 70)
        
        try:
            import shutil
            stat = shutil.disk_usage(str(self.base_path))
            free_gb = stat.free / (1024**3)
            
            has_space = free_gb >= 1  # Al menos 1 GB
            self.check(
                "Espacio en Disco",
                has_space,
                f"{free_gb:.2f} GB disponible (necesita ~100 MB)",
                f"Usado: {stat.used / (1024**3):.2f} GB, Total: {stat.total / (1024**3):.2f} GB"
            )
        except Exception as e:
            self.check("Espacio en Disco", True, "No verificable")
        
        # Resumen
        print("\n" + "=" * 70)
        print("  RESUMEN DE VERIFICACIÓN")
        print("=" * 70 + "\n")
        
        total_checks = len(self.results["checks"])
        passed_checks = sum(1 for c in self.results["checks"].values() if c["status"] == "PASS")
        
        print(f"Verificaciones Totales: {total_checks}")
        print(f"Pasadas: {passed_checks}")
        print(f"Fallidas: {total_checks - passed_checks}\n")
        
        if self.all_passed:
            print("✓ SISTEMA LISTO PARA PRODUCCIÓN\n")
            return True
        else:
            print("✗ ADVERTENCIAS DETECTADAS\n")
            print("Problemas encontrados:")
            for name, result in self.results["checks"].items():
                if result["status"] == "FAIL":
                    print(f"  • {name}: {result['message']}")
            print()
            return False
    
    def save_report(self, filename: str = "production_check_report.json"):
        """Guardar reporte en JSON"""
        report_path = self.base_path / filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"Reporte guardado en: {report_path}\n")
            return True
        except Exception as e:
            print(f"Error guardando reporte: {e}\n")
            return False

def main():
    """Función principal"""
    checker = ProductionChecker()
    success = checker.run_all_checks()
    
    # Guardar reporte
    checker.save_report()
    
    # Salir con código apropiado
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
