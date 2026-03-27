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
