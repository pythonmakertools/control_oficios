# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración BD
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'gestion_oficios'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres123')
    }
    
    # Carpetas
    CARPETA_BASE = os.getenv('CARPETA_BASE', 'C:\\gestion_oficios\\temp')
    CARPETA_NO_ASIGNADOS = os.getenv('CARPETA_NO_ASIGNADOS', 'C:\\gestion_oficios\\adjuntos\\no_asignados')
    CARPETA_ASIGNADOS = os.getenv('CARPETA_ASIGNADOS', 'C:\\gestion_oficios\\adjuntos\\asignados')
    CARPETA_ACUSES = os.getenv('CARPETA_ACUSES', 'C:\\gestion_oficios\\adjuntos\\acuses')
    
    # Correo
    SMTP_SERVER = os.getenv('SMTP_SERVER', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # Logging
    LOG_FILE = os.getenv('LOG_FILE', 'C:\\gestion_oficios\\logs\\servidor.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Server
    SERVER_IP = os.getenv('SERVER_IP', 'localhost')
    
    @classmethod
    def crear_carpetas(cls):
        """Crea las carpetas necesarias"""
        for carpeta in [cls.CARPETA_BASE, cls.CARPETA_NO_ASIGNADOS, 
                        cls.CARPETA_ASIGNADOS, cls.CARPETA_ACUSES]:
            Path(carpeta).mkdir(parents=True, exist_ok=True)
        
        # Carpeta de logs
        Path(cls.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)