#!/usr/bin/env python
"""
Punto de entrada para el ejecutable del cliente
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ejecutar el módulo cliente
from cliente.cliente import main

if __name__ == "__main__":
    main()