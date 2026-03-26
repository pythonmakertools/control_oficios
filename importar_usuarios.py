#!/usr/bin/env python
"""
Script para importar usuarios desde un archivo SQL o JSON
Ejecutar: python importar_usuarios.py backup_usuarios_20240101_120000.sql
"""

import os
import sys
import psycopg2

def importar_usuarios_sql(archivo_sql):
    """Importa usuarios desde archivo SQL"""
    
    # Configuración de la base de datos
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'gestion_oficios',
        'user': 'postgres',
        'password': 'postgres123'
    }
    
    print(f"Conectando a la base de datos...")
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Conexión exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    print(f"\nImportando usuarios desde: {archivo_sql}")
    try:
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        cursor.execute(sql)
        print("✅ Usuarios importados correctamente")
        
    except Exception as e:
        print(f"❌ Error al importar: {e}")
    
    finally:
        cursor.close()
        conn.close()

def importar_usuarios_json(archivo_json):
    """Importa usuarios desde archivo JSON"""
    import json
    
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'gestion_oficios',
        'user': 'postgres',
        'password': 'postgres123'
    }
    
    print(f"Conectando a la base de datos...")
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Conexión exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    print(f"\nImportando usuarios desde: {archivo_json}")
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        
        # Limpiar tabla
        cursor.execute("DELETE FROM usuarios WHERE id > 1;")
        cursor.execute("SELECT setval('usuarios_id_seq', 1, false);")
        
        # Insertar usuarios
        for u in usuarios:
            cursor.execute("""
                INSERT INTO usuarios 
                (username, password, nombre_completo, email, telefono, es_admin, activo, fecha_creacion, color_manual)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                u['username'],
                u['password'],
                u['nombre_completo'],
                u.get('email'),
                u.get('telefono'),
                u.get('es_admin', False),
                u.get('activo', True),
                u['fecha_creacion'],
                u.get('color_manual')
            ))
        
        print(f"✅ {len(usuarios)} usuarios importados correctamente")
        
    except Exception as e:
        print(f"❌ Error al importar: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_usuarios.py <archivo>")
        print("Ejemplo: python importar_usuarios.py backup_usuarios_20240101_120000.sql")
        sys.exit(1)
    
    archivo = sys.argv[1]
    
    if archivo.endswith('.sql'):
        importar_usuarios_sql(archivo)
    elif archivo.endswith('.json'):
        importar_usuarios_json(archivo)
    else:
        print("Formato no soportado. Use .sql o .json")
