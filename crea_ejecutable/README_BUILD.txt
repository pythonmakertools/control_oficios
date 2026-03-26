INSTRUCCIONES PARA CONSTRUIR EJECUTABLES
=========================================

1. INSTALAR DEPENDENCIAS
   pip install psycopg2-binary Pillow PyMuPDF openpyxl python-dotenv pyinstaller

2. VERIFICAR ENTORNO
   python check_build.py

3. CONSTRUIR EJECUTABLES
   Ejecutar como Administrador: build.bat

4. COPIAR ARCHIVO DE CONFIGURACIÓN
   Copiar .env a:
   - dist\GestionOficios_Cliente\.env
   - dist\GestionOficios_Servidor\.env

5. PROBAR EJECUTABLES
   - dist\GestionOficios_Cliente\GestionOficios_Cliente.exe
   - dist\GestionOficios_Servidor\GestionOficios_Servidor.exe

6. CREAR ACCESOS DIRECTOS
   Ejecutar: create_shortcuts.bat

POSIBLES PROBLEMAS Y SOLUCIONES
================================

Error: "No module named 'cliente'"
Solución: Asegurar que run_cliente.py está en la raíz

Error: "DLL load failed"
Solución: Instalar Microsoft Visual C++ Redistributable

Error: "psycopg2 not found"
Solución: pip install psycopg2-binary --force-reinstall

Error de permisos al construir
Solución: Ejecutar terminal como Administrador

Error de espacio en disco
Solución: Los ejecutables ocupan ~50-100 MB cada uno