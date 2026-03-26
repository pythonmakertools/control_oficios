#!/usr/bin/env python
"""
Script para exportar la tabla usuarios a un archivo SQL
Ejecutar: python exportar_usuarios.py
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

def exportar_usuarios():
    """Exporta los usuarios a archivos SQL y JSON"""
    
    # Configuración de la base de datos (ajustar según tu entorno)
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'gestion_oficios',
        'user': 'postgres',
        'password': 'postgres123'
    }
    
    print("Conectando a la base de datos...")
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Conexión exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # Exportar a SQL
    print("\nExportando usuarios a SQL...")
    try:
        cursor.execute("""
            SELECT id, username, password, nombre_completo, email, telefono, 
                   es_admin, activo, fecha_creacion, color_manual
            FROM usuarios 
            ORDER BY id
        """)
        usuarios = cursor.fetchall()
        
        # Crear archivo SQL
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sql_file = f"backup_usuarios_{timestamp}.sql"
        
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write("-- =============================================\n")
            f.write("-- BACKUP DE USUARIOS\n")
            f.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- =============================================\n\n")
            
            f.write("-- Eliminar usuarios existentes (excepto admin si es necesario)\n")
            f.write("DELETE FROM usuarios WHERE id > 1;\n\n")
            f.write("-- Restablecer secuencia\n")
            f.write("SELECT setval('usuarios_id_seq', 1, false);\n\n")
            
            f.write("-- Insertar usuarios\n")
            for u in usuarios:
                f.write(f"INSERT INTO usuarios (username, password, nombre_completo, email, telefono, es_admin, activo, fecha_creacion, color_manual) VALUES (\n")
                f.write(f"    '{u['username']}',\n")
                f.write(f"    '{u['password']}',\n")
                f.write(f"    '{u['nombre_completo']}',\n")
                f.write(f"    {f"'{u['email']}'" if u['email'] else 'NULL'},\n")
                f.write(f"    {f"'{u['telefono']}'" if u['telefono'] else 'NULL'},\n")
                f.write(f"    {u['es_admin']},\n")
                f.write(f"    {u['activo']},\n")
                f.write(f"    '{u['fecha_creacion']}',\n")
                f.write(f"    {f"'{u['color_manual']}'" if u['color_manual'] else 'NULL'}\n")
                f.write(f");\n\n")
        
        print(f"✅ SQL exportado a: {sql_file}")
        
        # Exportar a JSON
        json_file = f"backup_usuarios_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"✅ JSON exportado a: {json_file}")
        
        print(f"\n📊 Total de usuarios exportados: {len(usuarios)}")
        
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
    
    finally:
        cursor.close()
        conn.close()
        print("\n✅ Proceso completado")

if __name__ == "__main__":
    exportar_usuarios()
