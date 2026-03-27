control_oficios
Sistema de gestión de oficios con arquitectura cliente-servidor.

📋 Descripción
control_oficios es una aplicación que permite gestionar oficios mediante una arquitectura cliente-servidor. El proyecto está desarrollado en Python y utiliza PostgreSQL como base de datos.

🚀 Estado del Proyecto
✅ Versión inicial – Funcionalidades básicas implementadas

🛠️ Tecnologías utilizadas
Tecnología	Descripción
Python	Lenguaje principal
PostgreSQL	Base de datos
PL/pgSQL	Procedimientos almacenados
Batchfile	Scripts de automatización
Librerías principales:

psycopg2-binary – Conexión a PostgreSQL

python-dotenv – Variables de entorno

openpyxl – Manejo de Excel

matplotlib – Generación de gráficas

numpy – Cálculos numéricos

pillow – Procesamiento de imágenes

pymupdf – Manejo de PDF

📦 Instalación y Configuración
Requisitos previos
Python 3.8 o superior

PostgreSQL 12 o superior

pip (gestor de paquetes de Python)

Acceso administrativo para configuración de firewall (solo servidor)

🖥️ Configuración del Servidor
1. Estructura de carpetas
Crea las siguientes carpetas en el servidor:

bash
mkdir C:\gestion_oficios\adjuntos\no_asignados
mkdir C:\gestion_oficios\adjuntos\asignados
mkdir C:\gestion_oficios\adjuntos\acuses
mkdir C:\gestion_oficios\logs
mkdir C:\gestion_oficios\temp
mkdir C:\gestion_oficios\graficas
2. Crear entorno virtual e instalar dependencias
bash
cd C:\gestion_oficios
python -m venv venv
venv\Scripts\activate
pip install psycopg2-binary python-dotenv openpyxl matplotlib numpy pillow pymupdf
3. Configurar archivo .env en el servidor
Crea un archivo .env en la raíz del proyecto:

env
# Configuración del servidor
SERVER_IP=192.168.1.100  # IP REAL DEL SERVIDOR

# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestion_oficios
DB_USER=postgres
DB_PASSWORD=tu_contraseña

# Correo SMTP (Gmail ejemplo)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_contraseña_app

# Carpetas
CARPETA_BASE=C:\\gestion_oficios\\temp
CARPETA_NO_ASIGNADOS=C:\\gestion_oficios\\adjuntos\\no_asignados
CARPETA_ASIGNADOS=C:\\gestion_oficios\\adjuntos\\asignados
CARPETA_ACUSES=C:\\gestion_oficios\\adjuntos\\acuses

# Logging
LOG_FILE=C:\\gestion_oficios\\logs\\servidor.log
LOG_LEVEL=INFO
4. Configurar PostgreSQL
Crear base de datos:

bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE gestion_oficios;

# Conectar a la base de datos
\c gestion_oficios;

# Ejecutar script de esquema
\i C:\gestion_oficios\esquema.sql
Configurar acceso remoto (si el cliente está en otra máquina):

Editar postgresql.conf (ubicado típicamente en C:\Program Files\PostgreSQL\XX\data\):

conf
listen_addresses = '*'
Editar pg_hba.conf:

conf
# Permitir conexiones desde la red local
host    all             all             192.168.1.0/24          md5
Reiniciar PostgreSQL:

bash
net stop postgresql
net start postgresql
5. Configurar Firewall de Windows
Abrir puerto 5432 (PostgreSQL) para permitir conexiones remotas:

bash
netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=TCP localport=5432
Verificar que la regla se creó:

bash
netsh advfirewall firewall show rule name="PostgreSQL"
¿Por qué abrir el puerto 5432?
Este puerto permite que los clientes se conecten a la base de datos PostgreSQL desde otros equipos en la red. Sin esta regla, el firewall bloquearía las conexiones entrantes.

6. Verificar IP del servidor
bash
ipconfig
Busca "Dirección IPv4" (ejemplo: 192.168.1.100). Esta IP la usarás en la configuración del cliente.

7. Iniciar el servidor
bash
cd C:\gestion_oficios
venv\Scripts\activate
python -m servidor.servidor
Esperado:

Se abre una ventana de login

Login con admin / admin

Se muestra la interfaz principal del servidor

💻 Configuración del Cliente
1. Copiar el proyecto al cliente
Copia toda la carpeta C:\gestion_oficios al equipo cliente, o solo los archivos necesarios.

2. Crear entorno virtual e instalar dependencias
bash
cd C:\gestion_oficios
python -m venv venv
venv\Scripts\activate
pip install psycopg2-binary python-dotenv openpyxl matplotlib numpy pillow pymupdf
3. Configurar archivo .env en el cliente
env
# Configuración del cliente
SERVER_IP=192.168.1.100  # MISMA IP DEL SERVIDOR

# Base de datos (misma que servidor)
DB_PORT=5432
DB_NAME=gestion_oficios
DB_USER=postgres
DB_PASSWORD=tu_contraseña
4. Verificar conectividad con el servidor
Probar ping:

bash
ping 192.168.1.100
Probar puerto PostgreSQL:

bash
telnet 192.168.1.100 5432
Si telnet no está disponible, puedes instalarlo desde "Activar o desactivar características de Windows".

5. Iniciar el cliente
bash
cd C:\gestion_oficios
venv\Scripts\activate
python cliente.py
Esperado:

Conexión exitosa a la base de datos del servidor

Login con usuario normal

Muestra de oficios asignados

🧪 Testing (Cómo probar el proyecto)
Pruebas de conectividad
Prueba	Comando	Resultado esperado
Ping al servidor	ping 192.168.1.100	Respuesta exitosa
Puerto PostgreSQL	telnet 192.168.1.100 5432	Conexión establecida
Puerto servidor	telnet 192.168.1.100 5000	Conexión establecida (si aplica)
Pruebas funcionales
En el servidor:

Crear un usuario de prueba

Asignar un oficio a ese usuario

En el cliente:

Verificar que aparece el oficio asignado

Marcar el oficio como atendido

Verificar:

En el servidor, confirmar que el cambio de estado se refleja correctamente

Pruebas de scripts auxiliares
bash
python importar_usuarios.py
python exportar_usuarios.py
🔧 Solución de problemas comunes
Problema	Posible solución
"No se pudo conectar a BD"	Verificar IP, firewall, PostgreSQL está corriendo
"Connection refused"	PostgreSQL no acepta conexiones remotas. Revisar postgresql.conf y pg_hba.conf
"Password authentication failed"	Credenciales incorrectas en .env
"Module not found"	Ejecutar pip install -r requirements.txt con entorno virtual activado
El cliente no encuentra el servidor	Verificar que SERVER_IP en .env coincide con la IP real del servidor
Firewall bloquea conexión	Ejecutar el comando netsh advfirewall firewall add rule... nuevamente
📁 Estructura del proyecto
text
control_oficios/
├── cliente/
│   └── cliente.py
├── servidor/
│   └── servidor.py
├── crea_ejecutable/
├── esquema.sql
├── importar_usuarios.py
├── exportar_usuarios.py
├── requirements.txt
├── env_configura_ejemplo.txt
├── configuraciones.txt
└── directorios.txt
Carpetas creadas en el servidor:

text
C:\gestion_oficios\
├── adjuntos\
│   ├── no_asignados\
│   ├── asignados\
│   └── acuses\
├── logs\
├── temp\
├── graficas\
└── venv\
🤝 Contribuciones
Las contribuciones son bienvenidas. Para contribuir:

Haz un fork del proyecto

Crea una rama (git checkout -b feature/nueva-funcionalidad)

Realiza tus cambios y haz commit (git commit -m 'Añadir nueva funcionalidad')

Haz push (git push origin feature/nueva-funcionalidad)

Abre un Pull Request

📄 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

MANUAL DE CONSTRUCCIÓN DE EJECUTABLES
Sistema de Gestión de Oficios - Cliente y Servidor
📋 ÍNDICE
Estructura del Proyecto

Requisitos Previos

Instalación de Dependencias

Verificación del Entorno

Archivos de Configuración (.spec)

Puntos de Entrada (run_cliente.py / run_servidor.py)

Proceso de Construcción

Post-Construcción

Pruebas de los Ejecutables

Solución de Problemas

Resumen Rápido

1. ESTRUCTURA DEL PROYECTO
text
C:\gestion_oficios\
│
├── 📁 cliente/                    # Código fuente del cliente
├── 📁 servidor/                   # Código fuente del servidor
│   └── 📁 dialogs/                # Diálogos del servidor
│
├── 📁 dist/                       # Ejecutables generados (creado por PyInstaller)
│   ├── 📁 GestionOficios_Cliente/
│   │   ├── GestionOficios_Cliente.exe
│   │   └── .env
│   └── 📁 GestionOficios_Servidor/
│       ├── GestionOficios_Servidor.exe
│       └── .env
│
├── 📁 build/                      # Archivos temporales (se puede eliminar)
│
├── 🔧 run_cliente.py              # Punto de entrada para el cliente
├── 🔧 run_servidor.py             # Punto de entrada para el servidor
├── 🔧 cliente.spec                # Configuración PyInstaller - Cliente
├── 🔧 servidor.spec               # Configuración PyInstaller - Servidor
├── 🔧 build.bat                   # Script principal de construcción
├── 🔧 check_build.py              # Verificador de dependencias
├── 🔧 create_shortcuts.bat        # Creador de accesos directos
├── 🔧 test_db.py                  # Prueba de conexión a BD
├── 🔧 verificar_ejecutable.bat    # Verificador rápido
│
└── 📄 .env                        # Configuración (copiar a dist/)
2. REQUISITOS PREVIOS
Hardware
Espacio en disco: ~200 MB libres (para builds y ejecutables)

Memoria RAM: 2 GB recomendado

Software
Software	Versión	Notas
Python	3.8 o superior	Asegurar que está en PATH
pip	Última versión	Incluido con Python
PostgreSQL	12 o superior	Solo para pruebas de conexión
Visual C++ Redistributable	2015-2022	Necesario para psycopg2
Permisos
Ejecutar terminal como Administrador (para build.bat)

Acceso de lectura/escritura en C:\gestion_oficios

3. INSTALACIÓN DE DEPENDENCIAS
3.1 Abrir terminal como Administrador
cmd
# Presiona Win + X, luego selecciona "Terminal (Administrador)" o "CMD (Administrador)"
3.2 Navegar a la carpeta del proyecto
cmd
cd C:\gestion_oficios
3.3 Instalar todas las dependencias
cmd
pip install psycopg2-binary python-dotenv openpyxl matplotlib numpy pillow pymupdf pyinstaller
Explicación de cada dependencia:

Librería	Propósito
psycopg2-binary	Conexión a PostgreSQL
python-dotenv	Variables de entorno (.env)
openpyxl	Lectura/escritura de Excel
matplotlib	Generación de gráficas
numpy	Cálculos numéricos
pillow	Procesamiento de imágenes
pymupdf	Manejo de PDF
pyinstaller	Creación de ejecutables
3.4 Verificar instalación
cmd
pip list | findstr "psycopg2 dotenv openpyxl matplotlib numpy pillow pymupdf pyinstaller"
4. VERIFICACIÓN DEL ENTORNO
4.1 Ejecutar el verificador de dependencias
cmd
python check_build.py
Salida esperada:

text
==================================================
VERIFICACIÓN DE DEPENDENCIAS
==================================================

[REQUERIDOS]
  ✅ psycopg2
  ✅ psycopg2.extras
  ✅ PIL
  ✅ fitz
  ✅ openpyxl
  ✅ dotenv
  ✅ tkinter

[OPCIONALES]
  ✅ pyinstaller

==================================================
✅ Todo está listo para construir los ejecutables
==================================================
Si algún módulo aparece con ❌, instalarlo manualmente:

cmd
pip install <nombre_modulo>
5. ARCHIVOS DE CONFIGURACIÓN (.SPEC)
5.1 Archivo cliente.spec
Este archivo define cómo PyInstaller construye el ejecutable del cliente.

Ubicación: C:\gestion_oficios\cliente.spec

Contenido clave:

pathex: Ruta absoluta del proyecto

datas: Archivos y carpetas a incluir (.env, cliente/)

hiddenimports: Módulos que PyInstaller no detecta automáticamente

console=False: Ejecutable sin ventana de consola (solo GUI)

5.2 Archivo servidor.spec
Similar al del cliente, pero incluye:

Carpeta servidor/dialogs

Módulos adicionales: smtplib, email, matplotlib, numpy

5.3 Validar archivos .spec
Asegurar que PROJECT_ROOT apunte a la ruta correcta:

python
PROJECT_ROOT = r"C:\gestion_oficios"   # Cambiar si es otra ubicación
6. PUNTOS DE ENTRADA
6.1 run_cliente.py
python
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
6.2 run_servidor.py
python
#!/usr/bin/env python
"""
Punto de entrada para el ejecutable del servidor
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ejecutar el módulo servidor
from servidor.servidor import main

if __name__ == "__main__":
    main()
6.3 Verificar que los puntos de entrada funcionan
cmd
python run_cliente.py
python run_servidor.py
Ambos deben ejecutarse sin errores (pueden pedir conexión a BD, eso es normal).

7. PROCESO DE CONSTRUCCIÓN
7.1 Script build.bat (ejecutar como Administrador)
cmd
@echo off
echo ============================================
echo   CONSTRUCCIÓN DE EJECUTABLES
echo ============================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instale Python 3.8 o superior.
    pause
    exit /b 1
)
echo ✅ Python encontrado

REM Instalar/Actualizar PyInstaller
echo.
echo [2/5] Instalando PyInstaller...
pip install --upgrade pyinstaller
echo ✅ PyInstaller instalado

REM Verificar archivos necesarios
echo.
echo [3/5] Verificando archivos...
if not exist "run_cliente.py" (
    echo ❌ No se encuentra run_cliente.py
    pause
    exit /b 1
)
if not exist "run_servidor.py" (
    echo ❌ No se encuentra run_servidor.py
    pause
    exit /b 1
)
echo ✅ Archivos verificados

REM Limpiar builds anteriores
echo.
echo [4/5] Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec
echo ✅ Limpieza completada

REM Construir cliente
echo.
echo [5/5] Construyendo ejecutables...
echo    → Construyendo Cliente...
pyinstaller cliente.spec --clean --noconfirm
if errorlevel 1 (
    echo    ❌ Error construyendo Cliente
    pause
    exit /b 1
)
echo    ✅ Cliente construido

REM Construir servidor
echo    → Construyendo Servidor...
pyinstaller servidor.spec --clean --noconfirm
if errorlevel 1 (
    echo    ❌ Error construyendo Servidor
    pause
    exit /b 1
)
echo    ✅ Servidor construido

echo.
echo ============================================
echo   CONSTRUCCIÓN COMPLETADA
echo ============================================
echo.
echo 📁 Ejecutables generados en carpeta 'dist/'
echo.
echo   Cliente: dist\GestionOficios_Cliente\GestionOficios_Cliente.exe
echo   Servidor: dist\GestionOficios_Servidor\GestionOficios_Servidor.exe
echo.
echo ⚠️  IMPORTANTE: Copiar el archivo .env a la carpeta del ejecutable
echo.
pause
7.2 Ejecutar la construcción
cmd
# IMPORTANTE: Ejecutar como Administrador
cd C:\gestion_oficios
build.bat
7.3 Tiempo estimado de construcción
Componente	Tiempo aproximado
Cliente	2-5 minutos
Servidor	3-7 minutos
Total	5-12 minutos
7.4 Resultado esperado
text
dist/
├── GestionOficios_Cliente/
│   ├── GestionOficios_Cliente.exe
│   ├── .env (debes copiarlo)
│   └── cliente/ (carpeta con módulos)
└── GestionOficios_Servidor/
    ├── GestionOficios_Servidor.exe
    ├── .env (debes copiarlo)
    └── servidor/ (carpeta con módulos)
8. POST-CONSTRUCCIÓN
8.1 Copiar archivo .env a cada ejecutable
cmd
# Para el cliente
copy .env dist\GestionOficios_Cliente\.env

# Para el servidor
copy .env dist\GestionOficios_Servidor\.env
Importante: Editar cada .env según corresponda:

Cliente: SERVER_IP debe apuntar al servidor

Servidor: DB_HOST=localhost y credenciales correctas

8.2 Crear accesos directos en el escritorio
Ejecutar como Administrador:

cmd
create_shortcuts.bat
Archivo create_shortcuts.bat:

batch
@echo off
echo Creando accesos directos en el escritorio...

REM Cliente
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $shortcut = $ws.CreateShortcut('%userprofile%\Desktop\GestionOficios_Cliente.lnk'); $shortcut.TargetPath = '%~dp0dist\GestionOficios_Cliente\GestionOficios_Cliente.exe'; $shortcut.WorkingDirectory = '%~dp0dist\GestionOficios_Cliente'; $shortcut.Description = 'Gestión de Oficios - Cliente'; $shortcut.Save()"

REM Servidor
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $shortcut = $ws.CreateShortcut('%userprofile%\Desktop\GestionOficios_Servidor.lnk'); $shortcut.TargetPath = '%~dp0dist\GestionOficios_Servidor\GestionOficios_Servidor.exe'; $shortcut.WorkingDirectory = '%~dp0dist\GestionOficios_Servidor'; $shortcut.Description = 'Gestión de Oficios - Servidor'; $shortcut.Save()"

echo.
echo Accesos directos creados en el escritorio.
pause
9. PRUEBAS DE LOS EJECUTABLES
9.1 Prueba de conexión a BD
Ejecutar test_db.py desde la carpeta del ejecutable:

cmd
cd dist\GestionOficios_Servidor
python ..\..\test_db.py
Salida esperada:

text
==================================================
TEST DE CONEXIÓN A POSTGRESQL
==================================================

Configuración:
  Host: 192.168.1.100
  Puerto: 5432
  Base de datos: gestion_oficios
  Usuario: postgres

Conectando...
✅ Conexión exitosa!
   PostgreSQL: PostgreSQL 14.5...
9.2 Prueba rápida del ejecutable
Ejecutar verificar_ejecutable.bat:

cmd
cd dist\GestionOficios_Cliente
..\..\verificar_ejecutable.bat
9.3 Prueba manual
Servidor:

cmd
cd dist\GestionOficios_Servidor
GestionOficios_Servidor.exe
Debe abrir ventana de login

Login con admin/admin

Cliente:

cmd
cd dist\GestionOficios_Cliente
GestionOficios_Cliente.exe
Debe conectar al servidor

Login con usuario normal

10. SOLUCIÓN DE PROBLEMAS
10.1 Errores comunes y soluciones
Error	Causa	Solución
Python no encontrado	Python no está en PATH	Reinstalar Python marcando "Add to PATH"
No module named 'cliente'	Módulo no encontrado	Verificar que run_cliente.py está en la raíz
DLL load failed	Faltan DLLs de VC++	Instalar Visual C++ Redistributable
psycopg2 not found	Error en psycopg2	pip install psycopg2-binary --force-reinstall
Permission denied	Sin permisos de administrador	Ejecutar terminal como Administrador
Espacio insuficiente	Menos de 200 MB libres	Liberar espacio en disco
Error construyendo Cliente	Error en cliente.spec	Verificar rutas en PROJECT_ROOT
.env no encontrado	Archivo no copiado	Copiar .env a carpeta del ejecutable
10.2 Modo debug
Si el ejecutable falla sin mensaje, crear versión con consola visible:

Editar .spec temporalmente:

python
console=True,  # Cambiar a True para ver errores
Reconstruir:

cmd
pyinstaller cliente.spec --clean
10.3 Limpieza total para reconstruir
cmd
# Eliminar builds anteriores
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

# Reconstruir
build.bat
11. RESUMEN RÁPIDO
Flujo completo de construcción:
cmd
# 1. Abrir terminal como Administrador
# 2. Navegar al proyecto
cd C:\gestion_oficios

# 3. Instalar dependencias (solo la primera vez)
pip install psycopg2-binary python-dotenv openpyxl matplotlib numpy pillow pymupdf pyinstaller

# 4. Verificar entorno
python check_build.py

# 5. Construir ejecutables
build.bat

# 6. Copiar archivo .env
copy .env dist\GestionOficios_Cliente\.env
copy .env dist\GestionOficios_Servidor\.env

# 7. Crear accesos directos
create_shortcuts.bat

# 8. Probar
dist\GestionOficios_Servidor\GestionOficios_Servidor.exe
dist\GestionOficios_Cliente\GestionOficios_Cliente.exe
📝 NOTAS IMPORTANTES
Siempre ejecutar build.bat como Administrador

Los archivos .env deben copiarse manualmente después de cada build

Los ejecutables generados son portátiles (se pueden copiar a otras máquinas)

Los ejecutables pesan ~50-100 MB cada uno

Conservar los archivos .spec para futuras construcciones

📚 ARCHIVOS DE REFERENCIA
Archivo	Propósito
check_build.py	Verifica que todas las dependencias estén instaladas
test_db.py	Prueba la conexión a PostgreSQL con la configuración actual
verificar_ejecutable.bat	Prueba rápida que el ejecutable funciona
build.bat	Script principal de construcción
create_shortcuts.bat	Crea accesos directos en el escritorio

CÓMO CONSTRUIR ARCHIVOS .SPEC
¿Qué es un archivo .spec?
Un archivo .spec (specification) es un script de Python que le dice a PyInstaller exactamente cómo empaquetar tu aplicación. Contiene instrucciones sobre:

Qué archivos incluir

Qué módulos ocultos agregar

Dónde encontrar los recursos

Configuración del ejecutable final

MÉTODO 1: GENERAR AUTOMÁTICAMENTE (Punto de partida)
Paso 1: Crear el punto de entrada
Primero, asegúrate de tener los archivos run_cliente.py y run_servidor.py en la raíz:

run_cliente.py:

python
#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cliente.cliente import main

if __name__ == "__main__":
    main()
run_servidor.py:

python
#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from servidor.servidor import main

if __name__ == "__main__":
    main()
Paso 2: Generar .spec automático
cmd
cd C:\gestion_oficios

# Generar spec para el cliente
pyi-makespec --onefile --name "GestionOficios_Cliente" run_cliente.py

# Generar spec para el servidor
pyi-makespec --onefile --name "GestionOficios_Servidor" run_servidor.py
Esto crea:

GestionOficios_Cliente.spec

GestionOficios_Servidor.spec

Paso 3: Ver el contenido generado
cmd
type GestionOficios_Cliente.spec
MÉTODO 2: CONSTRUIR MANUALMENTE (Personalizado)
Este es el método que usaste en tu proyecto. Aquí te explico cómo se construye cada sección:

2.1 Estructura base de un .spec
python
# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# ============================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================
PROJECT_ROOT = r"C:\gestion_oficios"

# ============================================
# 2. MÓDULOS OCULTOS (HIDDEN IMPORTS)
# ============================================
hiddenimports = [
    # Librerías que PyInstaller no detecta automáticamente
    'psycopg2',
    'psycopg2.extras',
    'PIL',
    'PIL.Image',
    'fitz',
    # ... más módulos
]

# ============================================
# 3. ANÁLISIS (ANALYSIS)
# ============================================
a = Analysis(
    ['run_cliente.py'],           # Script principal
    pathex=[PROJECT_ROOT],        # Ruta de búsqueda
    binaries=[],                  # Archivos binarios adicionales (.dll, .so)
    datas=[                       # Archivos de datos a incluir
        (os.path.join(PROJECT_ROOT, '.env'), '.'),
        (os.path.join(PROJECT_ROOT, 'cliente'), 'cliente'),
    ],
    hiddenimports=hiddenimports,  # Módulos ocultos
    hookspath=[],                 # Hooks personalizados
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],                  # Módulos a excluir
    noarchive=False,
)

# ============================================
# 4. CREAR ARCHIVO PYZ (PYTHON ZIP)
# ============================================
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ============================================
# 5. CREAR EJECUTABLE (EXE)
# ============================================
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestionOficios_Cliente',   # Nombre del ejecutable
    debug=False,                      # Modo debug
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                         # Compresión UPX (opcional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                    # False = sin consola, True = con consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
3. CONSTRUCCIÓN PASO A PASO DE CADA SECCIÓN
Sección 1: hiddenimports (Módulos ocultos)
¿Por qué son necesarios?
PyInstaller analiza tu código buscando import statements, pero algunas librerías:

Se importan dinámicamente (ej: __import__('psycopg2'))

Son plugins que se cargan en tiempo de ejecución

Tienen submódulos que no se detectan automáticamente

Cómo identificar qué módulos agregar:

Ejecuta tu programa y mira errores:

text
ImportError: No module named 'psycopg2.extras'
→ Agregar 'psycopg2.extras' a hiddenimports

Revisa las dependencias de tus librerías:

python
# Si usas PIL, necesitas sus submódulos
'PIL',
'PIL.Image',
'PIL.ImageTk',
'PIL.ImageDraw',
Módulos comunes para proyectos con GUI:

python
'tkinter',
'tkinter.ttk',
'tkinter.messagebox',
'tkinter.filedialog',
Para tu proyecto Cliente:

python
hiddenimports = [
    # PostgreSQL
    'psycopg2',
    'psycopg2.extras',
    'psycopg2._psycopg',
    'psycopg2.extensions',
    # Imágenes
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    # PDF
    'fitz',
    # Excel
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.reader.excel',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    # Variables de entorno
    'dotenv',
    'dotenv.main',
    'dotenv.parser',
    # Módulos estándar (a veces necesarios)
    'mimetypes',
    'tempfile',
    'platform',
    'subprocess',
    'secrets',
    'hashlib',
    'threading',
    'json',
    'logging',
    'datetime',
    # Tkinter
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
]
Para tu proyecto Servidor (adicional al cliente):

python
hiddenimports = [
    # ... todo lo del cliente ...
    # Correo
    'smtplib',
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'email.mime.base',
    'email.encoders',
    # Gráficas
    'matplotlib',
    'matplotlib.backends',
    'matplotlib.backends.backend_tkagg',
    'numpy',
]
Sección 2: datas (Archivos de datos)
Sintaxis: (origen, destino_dentro_del_ejecutable)

python
datas = [
    # Archivo .env va en la raíz
    (os.path.join(PROJECT_ROOT, '.env'), '.'),
    
    # Toda la carpeta cliente va a "cliente/"
    (os.path.join(PROJECT_ROOT, 'cliente'), 'cliente'),
    
    # Subcarpetas específicas
    (os.path.join(PROJECT_ROOT, 'servidor', 'dialogs'), 'servidor/dialogs'),
]
Reglas importantes:

Usar os.path.join() para rutas

El destino usa / (incluso en Windows)

Si pones '.', el archivo va en la raíz del ejecutable

Sección 3: console (Ventana de consola)
python
console = False   # Sin consola (solo GUI) - recomendado para usuarios finales
console = True    # Con consola - útil para debugging
¿Cuándo usar cada uno?

False: Aplicación final, el usuario solo ve la ventana gráfica

True: Durante pruebas, para ver mensajes de error y logs

Sección 4: upx (Compresión)
python
upx = True   # Usar UPX para comprimir el ejecutable (reduce tamaño ~30-50%)
Requisito: Tener UPX instalado y en PATH, o en la misma carpeta que PyInstaller.

4. CONSTRUIR DESDE EL .SPEC
Usar el .spec para construir:
cmd
# Construir cliente
pyinstaller cliente.spec --clean --noconfirm

# Construir servidor
pyinstaller servidor.spec --clean --noconfirm
Explicación de parámetros:

Parámetro	Propósito
--clean	Limpia archivos temporales antes de construir
--noconfirm	No pregunta confirmación, sobrescribe automáticamente
--debug	Construye con información de depuración (opcional)
5. PLANTILLAS COMPLETAS PARA TU PROYECTO
Plantilla: cliente.spec
python
# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Ruta del proyecto (CAMBIAR SI ES DIFERENTE)
PROJECT_ROOT = r"C:\gestion_oficios"

# Módulos ocultos necesarios
hiddenimports = [
    'psycopg2',
    'psycopg2.extras',
    'psycopg2._psycopg',
    'psycopg2.extensions',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'fitz',
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.reader.excel',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'dotenv',
    'dotenv.main',
    'dotenv.parser',
    'mimetypes',
    'tempfile',
    'platform',
    'subprocess',
    'secrets',
    'hashlib',
    'threading',
    'json',
    'logging',
    'datetime',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
]

a = Analysis(
    ['run_cliente.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, '.env'), '.'),
        (os.path.join(PROJECT_ROOT, 'cliente'), 'cliente'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestionOficios_Cliente',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
Plantilla: servidor.spec
python
# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

PROJECT_ROOT = r"C:\gestion_oficios"

hiddenimports = [
    'psycopg2',
    'psycopg2.extras',
    'psycopg2._psycopg',
    'psycopg2.extensions',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'fitz',
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.reader.excel',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'dotenv',
    'dotenv.main',
    'dotenv.parser',
    'mimetypes',
    'tempfile',
    'platform',
    'subprocess',
    'secrets',
    'hashlib',
    'threading',
    'json',
    'logging',
    'datetime',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    # Servidor adicional
    'smtplib',
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'email.mime.base',
    'email.encoders',
    'matplotlib',
    'matplotlib.backends',
    'matplotlib.backends.backend_tkagg',
    'numpy',
]

a = Analysis(
    ['run_servidor.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, '.env'), '.'),
        (os.path.join(PROJECT_ROOT, 'servidor'), 'servidor'),
        (os.path.join(PROJECT_ROOT, 'servidor', 'dialogs'), 'servidor/dialogs'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestionOficios_Servidor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
6. COMANDOS ÚTILES PARA TRABAJAR CON .SPEC
Comando	Propósito
pyi-makespec run_cliente.py	Genera .spec básico
pyinstaller cliente.spec	Construye desde .spec
pyinstaller cliente.spec --clean	Limpia y construye
pyinstaller cliente.spec --debug	Construye con modo debug
pyinstaller --onefile run_cliente.py	Construye sin .spec (modo rápido)
7. ERRORES COMUNES AL CREAR .SPEC
Error	Causa	Solución
ModuleNotFoundError	Módulo no en hiddenimports	Agregar el módulo a la lista
FileNotFoundError: .env	.env no incluido en datas	Agregar ('.env', '.') a datas
No module named 'cliente'	Carpeta cliente no incluida	Agregar ('cliente', 'cliente') a datas
DLL load failed	Falta DLL en binaries	Agregar ruta de DLL a binaries
UPX is not available	UPX no instalado	Cambiar upx=False o instalar UPX
