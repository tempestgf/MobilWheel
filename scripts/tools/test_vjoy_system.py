#!/usr/bin/env python
"""
Test Script for vJoy Installation System
Prueba que el sistema de instalación de vJoy funciona correctamente
"""

import sys
from pathlib import Path

# Agregar el directorio del script al path
sys.path.insert(0, str(Path(__file__).parent))

def test_vjoy_system():
    """Ejecuta pruebas del sistema de vJoy"""
    
    print("=" * 70)
    print("  vJoy Installation System - Test Suite")
    print("=" * 70)
    print()
    
    # Test 1: Importaciones
    print("[TEST 1] Verificando importaciones...")
    try:
        from vjoy_installer import VjoyInstaller
        print("  ✓ vjoy_installer importado correctamente")
    except Exception as e:
        print(f"  ✗ Error importando vjoy_installer: {e}")
        return False
    
    try:
        from vjoy_setup_helper import VjoySetupHelper
        print("  ✓ vjoy_setup_helper importado correctamente")
    except Exception as e:
        print(f"  ✗ Error importando vjoy_setup_helper: {e}")
        return False
    
    try:
        from vjoy_bootstrap import check_and_setup_vjoy
        print("  ✓ vjoy_bootstrap importado correctamente")
    except Exception as e:
        print(f"  ✗ Error importando vjoy_bootstrap: {e}")
        return False
    
    print()
    
    # Test 2: VjoyInstaller
    print("[TEST 2] Probando VjoyInstaller...")
    try:
        installer = VjoyInstaller()
        
        print(f"  ✓ VjoyInstaller inicializado")
        print(f"    - Carpeta vJoy: {installer.vjoy_folder}")
        print(f"    - Arquitectura detectada: {installer.architecture}")
        print(f"    - Ruta existe: {installer.vjoy_folder.exists()}")
        
    except Exception as e:
        print(f"  ✗ Error con VjoyInstaller: {e}")
        return False
    
    print()
    
    # Test 3: VjoySetupHelper
    print("[TEST 3] Probando VjoySetupHelper...")
    try:
        helper = VjoySetupHelper()
        
        status = helper.check_vjoy_status()
        print(f"  ✓ VjoySetupHelper inicializado")
        print(f"    - Estado: {status}")
        print(f"    - Arquitectura: {helper.get_architecture()}")
        print(f"    - ¿Necesita instalación?: {helper.needs_installation()}")
        print(f"    - ¿Es administrador?: {helper.is_admin()}")
        
        vjoy_path = helper.get_vjoy_path()
        if vjoy_path:
            print(f"    - Ruta de vJoy: {vjoy_path}")
        
    except Exception as e:
        print(f"  ✗ Error con VjoySetupHelper: {e}")
        return False
    
    print()
    
    # Test 4: Archivos requeridos
    print("[TEST 4] Verificando archivos...")
    base_path = Path(__file__).parent
    
    required_files = [
        "vjoy_installer.py",
        "vjoy_setup_helper.py",
        "vjoy_bootstrap.py",
        "install_vjoy.bat",
        "Install-vJoy.ps1",
        "VJOY_INSTALLER_README.md",
        "QUICKSTART.md",
        "INTEGRATION_GUIDE.md"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (FALTA)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n  ⚠️  Faltan {len(missing_files)} archivo(s)")
    
    print()
    
    # Test 5: Carpeta vJoy
    print("[TEST 5] Verificando estructura de carpetas...")
    vjoy_dir = base_path / "vJoy"
    
    if vjoy_dir.exists():
        print(f"  ✓ Carpeta vJoy existe")
        
        if (vjoy_dir / "x86").exists():
            print(f"  ✓ Subcarpeta x86 existe")
        else:
            print(f"  ⚠️  Subcarpeta x86 no existe (se creará al descargar)")
        
        if (vjoy_dir / "x64").exists():
            print(f"  ✓ Subcarpeta x64 existe")
        else:
            print(f"  ⚠️  Subcarpeta x64 no existe (se creará al descargar)")
    else:
        print(f"  ✓ Carpeta vJoy será creada al descargar")
    
    print()
    
    # Test 6: Verificación de pyvjoy
    print("[TEST 6] Verificando pyvjoy...")
    try:
        import pyvjoy
        print(f"  ✓ pyvjoy está instalado (vJoy funciona)")
    except ImportError:
        print(f"  ℹ️  pyvjoy no está instalado (vJoy necesita ser instalado)")
    
    print()
    print("=" * 70)
    print("  ✓ Pruebas completadas")
    print("=" * 70)
    print()
    print("Próximos pasos:")
    print("  1. Ejecuta: install_vjoy.bat")
    print("  2. O ejecuta: python vjoy_installer.py")
    print("  3. Consulta QUICKSTART.md para más información")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_vjoy_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
