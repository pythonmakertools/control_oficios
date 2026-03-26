import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from .config import Config

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger(__name__)
    
    def conectar(self):
        """Conecta a la base de datos"""
        try:
            self.conn = psycopg2.connect(**Config.DB_CONFIG)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self.logger.info("Conexión a BD exitosa")
            return True
        except Exception as e:
            self.logger.error(f"Error conectando a BD: {e}")
            return False
    
    def cerrar(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()
    
    # ========== OFICIOS ==========
    def get_oficios(self, filtros=None):
        """Obtiene oficios con filtros opcionales"""
        query = """
            SELECT o.*, 
                   u.nombre_completo as asignado_nombre,
                   u.email as email_asignado,
                   (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'oficio') as tiene_archivo,
                   (SELECT COUNT(*) FROM archivos_binarios WHERE oficio_id = o.id AND tipo = 'acuse') as tiene_acuse,
                   CASE 
                       WHEN o.estado = 'En Proceso' AND o.fecha_asignacion IS NOT NULL 
                       THEN EXTRACT(DAY FROM (NOW() - o.fecha_asignacion))
                       ELSE 0
                   END as dias_proceso,
                   CASE 
                       WHEN o.estado = 'En Proceso' 
                       AND o.fecha_asignacion IS NOT NULL 
                       AND EXTRACT(DAY FROM (NOW() - o.fecha_asignacion)) > 3 
                       THEN TRUE
                       ELSE FALSE
                   END as vencido
            FROM oficios o 
            LEFT JOIN usuarios u ON o.usuario_asignado_id = u.id
            WHERE 1=1
        """
        params = []
        
        if filtros:
            if filtros.get('estado') and filtros['estado'] != "Todos":
                query += " AND o.estado = %s"
                params.append(filtros['estado'])
            
            if filtros.get('usuario') and filtros['usuario'] != "Todos":
                query += " AND u.username = %s"
                params.append(filtros['usuario'])
            
            if filtros.get('busqueda'):
                query += " AND (o.numero_oficio ILIKE %s OR o.remitente ILIKE %s OR o.asunto ILIKE %s)"
                busqueda = f"%{filtros['busqueda']}%"
                params.extend([busqueda, busqueda, busqueda])
            
            if filtros.get('solo_activos'):
                query += " AND o.estado IN ('En Proceso')"
        
        query += " ORDER BY o.fecha_creacion DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_oficio_by_id(self, oficio_id):
        """Obtiene un oficio por ID"""
        self.cursor.execute("""
            SELECT o.*, u.nombre_completo as asignado, u2.nombre_completo as creador,
                   u.username as username_asignado, u.email as email_asignado
            FROM oficios o
            LEFT JOIN usuarios u ON o.usuario_asignado_id = u.id
            LEFT JOIN usuarios u2 ON o.created_by = u2.id
            WHERE o.id = %s
        """, (oficio_id,))
        return self.cursor.fetchone()
    
    def insert_oficio(self, datos, usuario_id):
        """Inserta un nuevo oficio"""
        self.cursor.execute("""
            INSERT INTO oficios 
            (numero_oficio, fecha_oficio, remitente, destinatario, asunto, 
             tipo_oficio, prioridad, ruta_archivo, created_by, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            datos.get('numero_oficio'),
            datos.get('fecha_oficio'),
            datos.get('remitente'),
            datos.get('destinatario'),
            datos.get('asunto'),
            datos.get('tipo_oficio', 'Oficio'),
            datos.get('prioridad', 'Normal'),
            datos.get('ruta_archivo'),
            usuario_id,
            datos.get('estado', 'En Proceso')
        ))
        return self.cursor.fetchone()['id']
    
    def update_oficio(self, oficio_id, datos):
        """Actualiza un oficio"""
        campos = []
        valores = []
        
        campos_actualizables = [
            'numero_oficio', 'fecha_oficio', 'remitente', 'destinatario', 
            'asunto', 'tipo_oficio', 'prioridad', 'estado', 'acuse_recibido',
            'oficio_respuesta', 'notas', 'usuario_asignado_id'
        ]
        
        for campo in campos_actualizables:
            if campo in datos:
                campos.append(f"{campo} = %s")
                valores.append(datos[campo])
        
        if 'fecha_atendido' in datos and datos['estado'] == 'Atendido':
            campos.append("fecha_atendido = NOW()")
        
        if not campos:
            return False
        
        query = f"UPDATE oficios SET {', '.join(campos)} WHERE id = %s"
        valores.append(oficio_id)
        
        self.cursor.execute(query, valores)
        return True
    
    def delete_oficio(self, oficio_id):
        """Elimina un oficio"""
        self.cursor.execute("DELETE FROM oficios WHERE id = %s", (oficio_id,))
        return True
    
    def asignar_oficio(self, oficio_id, usuario_id):
        """Asigna un oficio a un usuario"""
        self.cursor.execute("""
            UPDATE oficios 
            SET usuario_asignado_id = %s, fecha_asignacion = NOW(), estado = 'En Proceso'
            WHERE id = %s
        """, (usuario_id, oficio_id))
        return True
    
    # ========== USUARIOS ==========
    def get_usuarios(self, solo_activos=True):
        """Obtiene lista de usuarios"""
        query = "SELECT * FROM usuarios"
        if solo_activos:
            query += " WHERE activo = TRUE"
        query += " ORDER BY nombre_completo"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_usuarios_no_admin(self, solo_activos=True):
        """Obtiene usuarios no administradores"""
        query = "SELECT * FROM usuarios WHERE es_admin = FALSE"
        if solo_activos:
            query += " AND activo = TRUE"
        query += " ORDER BY nombre_completo"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_usuario_by_id(self, usuario_id):
        """Obtiene un usuario por ID"""
        self.cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
        return self.cursor.fetchone()
    
    def get_usuario_by_username(self, username):
        """Obtiene un usuario por username"""
        self.cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        return self.cursor.fetchone()
    
    def insert_usuario(self, datos):
        """Inserta un nuevo usuario"""
        self.cursor.execute("""
            INSERT INTO usuarios 
            (username, password, nombre_completo, email, telefono, es_admin)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            datos['username'],
            datos['password'],
            datos['nombre_completo'],
            datos.get('email'),
            datos.get('telefono'),
            datos.get('es_admin', False)
        ))
        return self.cursor.fetchone()['id']
    
    def update_usuario(self, usuario_id, datos):
        """Actualiza un usuario"""
        campos = []
        valores = []
        
        campos_actualizables = [
            'username', 'nombre_completo', 'email', 'telefono', 'es_admin', 'activo', 'color_manual'
        ]
        
        for campo in campos_actualizables:
            if campo in datos:
                campos.append(f"{campo} = %s")
                valores.append(datos[campo])
        
        if 'password' in datos and datos['password']:
            campos.append("password = %s")
            valores.append(datos['password'])
        
        if not campos:
            return False
        
        query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = %s"
        valores.append(usuario_id)
        
        self.cursor.execute(query, valores)
        return True
    
    def delete_usuario(self, usuario_id):
        """Elimina un usuario"""
        self.cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        return True
    
    def login_usuario(self, username, password, admin_required=True):
        """Valida login de usuario"""
        query = """
            SELECT * FROM usuarios 
            WHERE username = %s AND password = %s AND activo = TRUE
        """
        if admin_required:
            query += " AND es_admin = TRUE"
        
        self.cursor.execute(query, (username, password))
        return self.cursor.fetchone()
    
    # ========== ARCHIVOS BINARIOS ==========
    def guardar_archivo(self, oficio_id, tipo, nombre_archivo, contenido_bytes, usuario_id):
        """Guarda un archivo en la BD"""
        import hashlib
        import mimetypes
        
        mime_type = mimetypes.guess_type(nombre_archivo)[0] or 'application/octet-stream'
        hash_md5 = hashlib.md5(contenido_bytes).hexdigest()
        
        self.cursor.execute("""
            INSERT INTO archivos_binarios 
            (oficio_id, tipo, nombre_archivo, contenido, mime_type, tamanio, usuario_id, hash_md5)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            oficio_id,
            tipo,
            nombre_archivo,
            psycopg2.Binary(contenido_bytes),
            mime_type,
            len(contenido_bytes),
            usuario_id,
            hash_md5
        ))
        return True
    
    def get_archivo(self, oficio_id, tipo='oficio'):
        """Obtiene un archivo de la BD"""
        self.cursor.execute("""
            SELECT nombre_archivo, contenido FROM archivos_binarios 
            WHERE oficio_id = %s AND tipo = %s
            ORDER BY fecha_subida DESC LIMIT 1
        """, (oficio_id, tipo))
        return self.cursor.fetchone()
    
    # ========== ESTADÍSTICAS ==========
    def get_estadisticas(self):
        """Obtiene estadísticas generales"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN estado = 'En Proceso' THEN 1 END) as en_proceso,
                COUNT(CASE WHEN estado = 'Atendido' THEN 1 END) as atendidos,
                COUNT(CASE WHEN estado = 'Archivado' THEN 1 END) as archivados,
                COUNT(CASE 
                    WHEN estado = 'En Proceso' 
                    AND fecha_asignacion IS NOT NULL 
                    AND EXTRACT(DAY FROM (NOW() - fecha_asignacion)) > 3 
                    THEN 1 
                END) as vencidos
            FROM oficios
        """)
        return self.cursor.fetchone()
    
    def get_estadisticas_usuarios(self):
        """Obtiene estadísticas por usuario"""
        self.cursor.execute("""
            SELECT 
                u.id,
                u.nombre_completo,
                u.color_manual,
                COUNT(o.id) as total_asignados,
                COUNT(CASE WHEN o.estado = 'En Proceso' THEN 1 END) as en_proceso,
                COUNT(CASE WHEN o.estado = 'Atendido' THEN 1 END) as atendidos,
                COUNT(CASE WHEN o.estado = 'Archivado' THEN 1 END) as archivados,
                COUNT(CASE 
                    WHEN o.estado = 'En Proceso' 
                    AND o.fecha_asignacion IS NOT NULL 
                    AND EXTRACT(DAY FROM (NOW() - o.fecha_asignacion)) > 3 
                    THEN 1 
                END) as vencidos,
                MAX(CASE 
                    WHEN o.estado = 'En Proceso' 
                    AND o.fecha_asignacion IS NOT NULL 
                    AND EXTRACT(DAY FROM (NOW() - o.fecha_asignacion)) > 3 
                    THEN 1 
                    ELSE 0 
                END) as tiene_vencidos
            FROM usuarios u
            LEFT JOIN oficios o ON u.id = o.usuario_asignado_id
            WHERE u.activo = TRUE AND u.es_admin = FALSE
            GROUP BY u.id, u.nombre_completo, u.color_manual
            ORDER BY u.nombre_completo
        """)
        return self.cursor.fetchall()
    
    def get_tendencias(self, dias=30):
        """Obtiene tendencias temporales"""
        self.cursor.execute("""
            SELECT 
                DATE(fecha_creacion) as fecha,
                COUNT(*) as total,
                COUNT(CASE WHEN estado = 'En Proceso' THEN 1 END) as proceso,
                COUNT(CASE WHEN estado = 'Atendido' THEN 1 END) as atendido
            FROM oficios
            WHERE fecha_creacion >= CURRENT_DATE - %s::integer
            GROUP BY DATE(fecha_creacion)
            ORDER BY fecha
        """, (dias,))
        return self.cursor.fetchall()