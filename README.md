control_oficios
Sistema de gestión de oficios con arquitectura cliente-servidor.

📋 Descripción
control_oficios es una aplicación que permite gestionar oficios mediante una arquitectura cliente-servidor. El proyecto está desarrollado en Python y utiliza PostgreSQL como base de datos.

🚀 Estado del Proyecto
✅ Versión inicial – Funcionalidades básicas implementadas

🛠️ Tecnologías utilizadas
Tecnología	Descripción
Python	Lenguaje principal (94.5%)
PL/pgSQL	Procedimientos almacenados (4.4%)
Batchfile	Scripts de automatización (1.1%)
PostgreSQL	Base de datos
📦 Instalación
Requisitos previos
Python 3.8 o superior

PostgreSQL 12 o superior

pip (gestor de paquetes de Python)

Pasos
Clonar el repositorio

bash
git clone https://github.com/pythonmakertools/control_oficios.git
cd control_oficios
Crear y activar entorno virtual (recomendado)

bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
Instalar dependencias

bash
pip install -r requirements.txt
Configurar variables de entorno

Copia el archivo env_configura_ejemplo.txt a .env

Edita .env con tus credenciales de base de datos

Configurar la base de datos

Ejecuta el script esquema.sql en PostgreSQL para crear las tablas necesarias.

💻 Uso
El sistema consta de dos partes principales:

Iniciar el servidor
bash
cd servidor
python servidor.py
Iniciar el cliente
bash
cd cliente
python cliente.py
Scripts auxiliares
importar_usuarios.py – Importa usuarios al sistema

exportar_usuarios.py – Exporta datos de usuarios

🧪 Testing (Cómo probar el proyecto)
Importante: Se debe verificar el correcto funcionamiento de la comunicación cliente-servidor y las operaciones de base de datos.

1. Prueba de conexión servidor
bash
cd servidor
python servidor.py
Esperado: El servidor inicia y muestra un mensaje indicando que está escuchando conexiones.

2. Prueba de cliente básico
En otra terminal:

bash
cd cliente
python cliente.py
Esperado: El cliente se conecta exitosamente al servidor.

3. Prueba de scripts de usuario
bash
python importar_usuarios.py
python exportar_usuarios.py
Esperado: Los scripts se ejecutan sin errores y muestran los resultados esperados.

4. Prueba de base de datos
Conéctate a PostgreSQL y verifica que las tablas se crearon correctamente con esquema.sql

Ejecuta consultas básicas para confirmar la estructura

5. Prueba de integración completa
Realiza una operación completa desde el cliente que involucre consulta/inserción en la base de datos

Verifica los logs del servidor para confirmar que no hay errores

🤝 Contribuciones
Las contribuciones son bienvenidas. Para contribuir:

Haz un fork del proyecto

Crea una rama para tu funcionalidad (git checkout -b feature/nueva-funcionalidad)

Realiza tus cambios y haz commit (git commit -m 'Añadir nueva funcionalidad')

Haz push a la rama (git push origin feature/nueva-funcionalidad)

Abre un Pull Request

📄 Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

📁 Estructura del proyecto
text
control_oficios/
├── cliente/            # Código del lado cliente
├── servidor/           # Código del lado servidor
├── crea_ejecutable/    # Scripts para crear ejecutables
├── esquema.sql         # Definición de la base de datos
├── importar_usuarios.py
├── exportar_usuarios.py
├── requirements.txt    # Dependencias de Python
└── configuraciones.txt # Configuraciones adicionales
