#!/usr/bin/env python
"""
Verificador de dependencias antes de construir el ejecutable
"""

import sys
import importlib

def check_module(module_name):
    """Verifica si un módulo está instalado"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 50)
    print("VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 50)
    
    required_modules = [
        'psycopg2',
        'psycopg2.extras',
        'PIL',
        'fitz',
        'openpyxl',
        'dotenv',
        'tkinter',
    ]
    
    optional_modules = [
        'pyinstaller',
    ]
    
    print("\n[REQUERIDOS]")
    all_ok = True
    for mod in required_modules:
        ok = check_module(mod)
        status = "✅" if ok else "❌"
        print(f"  {status} {mod}")
        if not ok:
            all_ok = False
    
    print("\n[OPCIONALES]")
    for mod in optional_modules:
        ok = check_module(mod)
        status = "✅" if ok else "❌"
        print(f"  {status} {mod}")
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ Todo está listo para construir los ejecutables")
    else:
        print("❌ Faltan dependencias. Instale con:")
        print("   pip install psycopg2-binary Pillow PyMuPDF openpyxl python-dotenv")
    print("=" * 50)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())