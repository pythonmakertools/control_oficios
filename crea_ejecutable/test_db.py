# test_db.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def test_conexion():
    print("=" * 50)
    print("TEST DE CONEXIÓN A POSTGRESQL")
    print("=" * 50)
    
    db_config = {
        'host': os.getenv('SERVER_IP', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'gestion_oficios'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres123')
    }
    
    print(f"\nConfiguración:")
    print(f"  Host: {db_config['host']}")
    print(f"  Puerto: {db_config['port']}")
    print(f"  Base de datos: {db_config['database']}")
    print(f"  Usuario: {db_config['user']}")
    
    try:
        print("\nConectando...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Conexión exitosa!")
        print(f"   PostgreSQL: {version['version'][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\nPosibles soluciones:")
        print("  1. Verificar que PostgreSQL esté corriendo")
        print("  2. Verificar el archivo .env con los datos correctos")
        print("  3. Verificar firewall")
        return False

if __name__ == "__main__":
    test_conexion()
    input("\nPresiona Enter para salir...")