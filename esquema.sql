-- =============================================
-- ESQUEMA COMPLETO - GESTIÓN DE OFICIOS
-- VERSIÓN FINAL ACTUALIZADA
-- =============================================

-- Conectar a la base de datos
-- \c gestion_oficios;

-- =============================================
-- ELIMINAR TABLAS EXISTENTES (ORDEN CORRECTO)
-- =============================================
DROP TABLE IF EXISTS archivos_binarios CASCADE;
DROP TABLE IF EXISTS historial_oficios CASCADE;
DROP TABLE IF EXISTS archivos_oficio CASCADE;
DROP TABLE IF EXISTS sesiones_activas CASCADE;
DROP TABLE IF EXISTS oficios_informales CASCADE;
DROP TABLE IF EXISTS oficios CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- =============================================
-- TABLA DE USUARIOS
-- =============================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    es_admin BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    color_manual VARCHAR(10) DEFAULT NULL -- 'verde' para omisiones
);

-- =============================================
-- TABLA DE OFICIOS (PRINCIPAL) - ASIGNADOS POR ADMIN
-- =============================================
CREATE TABLE oficios (
    id SERIAL PRIMARY KEY,
    numero_oficio VARCHAR(50) NOT NULL,
    fecha_oficio DATE NOT NULL,
    remitente VARCHAR(200) NOT NULL,
    destinatario VARCHAR(200) NOT NULL,
    asunto TEXT NOT NULL,
    descripcion TEXT,
    tipo_oficio VARCHAR(50) DEFAULT 'Oficio',
    prioridad VARCHAR(20) DEFAULT 'Normal',
    
    -- Estados del flujo
    estado VARCHAR(50) DEFAULT 'En Proceso', -- En Proceso, Atendido, Archivado
    fecha_inicio_tramite TIMESTAMP,
    fecha_atendido TIMESTAMP,
    
    -- Asignación
    usuario_asignado_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    fecha_asignacion TIMESTAMP,
    
    -- Archivos
    ruta_archivo VARCHAR(500),
    ruta_acuse VARCHAR(500),
    acuse_recibido BOOLEAN DEFAULT FALSE,
    oficio_respuesta TEXT,
    notas TEXT,
    
    -- Metadatos
    created_by INTEGER REFERENCES usuarios(id),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    año_oficio INTEGER
);

-- =============================================
-- TABLA DE OFICIOS INFORMALES (CREADOS POR USUARIOS)
-- =============================================
CREATE TABLE oficios_informales (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Datos principales
    numero_oficio VARCHAR(50),                    -- Número del oficio (obligatorio)
    fecha_recepcion DATE NOT NULL,                -- Fecha de ingreso
    asunto TEXT NOT NULL,                         -- Asunto del oficio
    canal VARCHAR(50) DEFAULT 'WhatsApp',         -- Canal de recepción
    
    -- Campos opcionales
    remitente VARCHAR(200),                       -- Remitente (opcional)
    destinatario VARCHAR(200),                    -- Destinatario (opcional)
    descripcion TEXT,                             -- Descripción adicional
    fecha_entrega DATE,                           -- Fecha límite esperada
    requiere_seguimiento BOOLEAN DEFAULT FALSE,   -- Requiere seguimiento
    fecha_seguimiento DATE,                       -- Fecha de seguimiento programada
    
    -- Estados y seguimiento
    estado VARCHAR(50) DEFAULT 'Pendiente',       -- Pendiente, Atendido, Archivado
    fecha_respuesta TIMESTAMP,                    -- Fecha cuando se marcó atendido
    oficio_respuesta TEXT,                        -- Número de oficio de respuesta
    notas TEXT,                                   -- Notas adicionales
    
    -- Metadatos
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- TABLA DE ARCHIVOS BINARIOS
-- =============================================
CREATE TABLE archivos_binarios (
    id SERIAL PRIMARY KEY,
    oficio_id INTEGER REFERENCES oficios(id) ON DELETE CASCADE,
    oficio_informal_id INTEGER REFERENCES oficios_informales(id) ON DELETE CASCADE,
    tipo VARCHAR(30) NOT NULL,  -- 'oficio', 'acuse', 'acuse_informal'
    nombre_archivo VARCHAR(255) NOT NULL,
    contenido BYTEA NOT NULL,
    mime_type VARCHAR(100),
    tamanio INTEGER,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id),
    hash_md5 VARCHAR(32),
    
    -- Asegurar que al menos una referencia existe
    CONSTRAINT archivo_referencia_check CHECK (
        (oficio_id IS NOT NULL AND oficio_informal_id IS NULL) OR
        (oficio_id IS NULL AND oficio_informal_id IS NOT NULL)
    )
);

-- =============================================
-- TABLA DE ARCHIVOS (COMPATIBILIDAD)
-- =============================================
CREATE TABLE archivos_oficio (
    id SERIAL PRIMARY KEY,
    oficio_id INTEGER REFERENCES oficios(id) ON DELETE CASCADE,
    tipo VARCHAR(50),
    nombre_archivo VARCHAR(255),
    ruta_completa VARCHAR(500),
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id)
);

-- =============================================
-- TABLA DE SESIONES
-- =============================================
CREATE TABLE sesiones_activas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    token_sesion VARCHAR(255) UNIQUE NOT NULL,
    dispositivo VARCHAR(255),
    ip_address VARCHAR(45),
    fecha_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP,
    activa BOOLEAN DEFAULT TRUE
);

-- =============================================
-- TABLA DE HISTORIAL
-- =============================================
CREATE TABLE historial_oficios (
    id SERIAL PRIMARY KEY,
    oficio_id INTEGER REFERENCES oficios(id) ON DELETE CASCADE,
    oficio_informal_id INTEGER REFERENCES oficios_informales(id) ON DELETE CASCADE,
    usuario_id INTEGER REFERENCES usuarios(id),
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50),
    acuse_anterior BOOLEAN,
    acuse_nuevo BOOLEAN,
    notas TEXT,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- TABLA DE OMISIONES (para colores manuales)
-- =============================================
CREATE TABLE omisiones_color (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_omision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    aplicado_por INTEGER REFERENCES usuarios(id)
);

-- =============================================
-- ÍNDICES PARA RENDIMIENTO
-- =============================================
CREATE INDEX idx_oficios_usuario ON oficios(usuario_asignado_id);
CREATE INDEX idx_oficios_estado ON oficios(estado);
CREATE INDEX idx_oficios_fecha ON oficios(fecha_oficio);
CREATE INDEX idx_oficios_anio ON oficios(año_oficio);

CREATE INDEX idx_informales_usuario ON oficios_informales(usuario_id);
CREATE INDEX idx_informales_estado ON oficios_informales(estado);
CREATE INDEX idx_informales_numero ON oficios_informales(numero_oficio);

CREATE INDEX idx_sesiones_token ON sesiones_activas(token_sesion);
CREATE INDEX idx_archivos_oficio ON archivos_binarios(oficio_id);
CREATE INDEX idx_archivos_informal ON archivos_binarios(oficio_informal_id);
CREATE INDEX idx_archivos_tipo ON archivos_binarios(tipo);

-- =============================================
-- CONSTRAINT UNIQUE (número + usuario para informales)
-- =============================================
ALTER TABLE oficios DROP CONSTRAINT IF EXISTS unique_numero_oficio_anio;
ALTER TABLE oficios ADD CONSTRAINT unique_numero_oficio_anio UNIQUE (numero_oficio, año_oficio);

-- Para oficios_informales, un usuario no puede tener dos oficios con el mismo número
ALTER TABLE oficios_informales DROP CONSTRAINT IF EXISTS unique_informal_numero_usuario;
ALTER TABLE oficios_informales ADD CONSTRAINT unique_informal_numero_usuario UNIQUE (numero_oficio, usuario_id);

-- =============================================
-- FUNCIÓN PARA ACTUALIZAR FECHA (oficios)
-- =============================================
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_oficios_fecha ON oficios;
CREATE TRIGGER update_oficios_fecha
    BEFORE UPDATE ON oficios
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- =============================================
-- FUNCIÓN PARA ACTUALIZAR FECHA (informales)
-- =============================================
DROP TRIGGER IF EXISTS update_informales_fecha ON oficios_informales;
CREATE TRIGGER update_informales_fecha
    BEFORE UPDATE ON oficios_informales
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- =============================================
-- FUNCIÓN PARA ACTUALIZAR AÑO (oficios)
-- =============================================
CREATE OR REPLACE FUNCTION update_año_oficio()
RETURNS TRIGGER AS $$
BEGIN
    NEW.año_oficio = EXTRACT(YEAR FROM NEW.fecha_oficio);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_año_oficio ON oficios;
CREATE TRIGGER set_año_oficio
    BEFORE INSERT OR UPDATE OF fecha_oficio ON oficios
    FOR EACH ROW
    EXECUTE FUNCTION update_año_oficio();

-- =============================================
-- FUNCIÓN PARA HISTORIAL (oficios)
-- =============================================
CREATE OR REPLACE FUNCTION guardar_historial()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.estado IS DISTINCT FROM NEW.estado OR 
       OLD.acuse_recibido IS DISTINCT FROM NEW.acuse_recibido THEN
        INSERT INTO historial_oficios 
            (oficio_id, usuario_id, estado_anterior, estado_nuevo, 
             acuse_anterior, acuse_nuevo, notas)
        VALUES 
            (NEW.id, NEW.usuario_asignado_id, OLD.estado, NEW.estado,
             OLD.acuse_recibido, NEW.acuse_recibido, 'Cambio automático');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_historial ON oficios;
CREATE TRIGGER trigger_historial
    AFTER UPDATE ON oficios
    FOR EACH ROW
    EXECUTE FUNCTION guardar_historial();

-- =============================================
-- FUNCIÓN PARA HISTORIAL (informales)
-- =============================================
CREATE OR REPLACE FUNCTION guardar_historial_informal()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.estado IS DISTINCT FROM NEW.estado THEN
        INSERT INTO historial_oficios 
            (oficio_informal_id, usuario_id, estado_anterior, estado_nuevo, notas)
        VALUES 
            (NEW.id, NEW.usuario_id, OLD.estado, NEW.estado, 
             'Cambio de estado en oficio informal');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_historial_informal ON oficios_informales;
CREATE TRIGGER trigger_historial_informal
    AFTER UPDATE ON oficios_informales
    FOR EACH ROW
    EXECUTE FUNCTION guardar_historial_informal();

-- =============================================
-- INSERTAR USUARIOS DE PRUEBA
-- =============================================
INSERT INTO usuarios (username, password, nombre_completo, email, es_admin) VALUES 
('admin', '123456', 'Administrador Sistema', 'admin@oficios.local', TRUE),
('juan', '123456', 'Juan Pérez', 'juan@oficios.local', FALSE),
('maria', '123456', 'María López', 'maria@oficios.local', FALSE),
('carlos', '123456', 'Carlos Rodríguez', 'carlos@oficios.local', FALSE),
('ana', '123456', 'Ana Martínez', 'ana@oficios.local', FALSE),
('ramon', '123456', 'Ramón', 'ramon@oficios.local', FALSE),
('paolo', '123456', 'Paolo', 'paolo@oficios.local', FALSE),
('jesus', '123456', 'Jesús', 'jesus@oficios.local', FALSE),
('nancy', '123456', 'Nancy', 'nancy@oficios.local', FALSE),
('fernando', '123456', 'Fernando', 'fernando@oficios.local', FALSE),
('angel', '123456', 'Ángel', 'angel@oficios.local', FALSE);

-- =============================================
-- INSERTAR OFICIOS DE PRUEBA (formales)
-- =============================================
INSERT INTO oficios (numero_oficio, fecha_oficio, remitente, destinatario, asunto, 
                     tipo_oficio, prioridad, estado, created_by, usuario_asignado_id, acuse_recibido,
                     fecha_asignacion)
VALUES 
('OF-2025-001', '2025-01-15', 'Secretaría General', 'Departamento Legal', 
 'Revisión de contratos', 'Oficio', 'Alta', 'Atendido', 1, 2, TRUE, NOW() - INTERVAL '10 days'),

('OF-2025-002', '2025-01-20', 'Recursos Humanos', 'Todos los departamentos', 
 'Convocatoria a reunión', 'Circular', 'Normal', 'En Proceso', 1, NULL, FALSE, NULL),

('OF-2025-003', '2025-02-01', 'Gerencia', 'Departamento Sistemas', 
 'Actualización de software', 'Memorandum', 'Alta', 'En Proceso', 1, 3, FALSE, NOW() - INTERVAL '5 days'),

('OF-2025-004', '2025-02-10', 'Proveedor externo', 'Compras', 
 'Cotización de materiales', 'Oficio', 'Baja', 'Atendido', 1, 4, TRUE, NOW() - INTERVAL '2 days'),

('OF-2025-005', '2025-02-15', 'Cliente importante', 'Atención al cliente', 
 'Queja por servicio', 'Oficio', 'Alta', 'En Proceso', 1, 2, FALSE, NOW() - INTERVAL '8 days');

-- =============================================
-- INSERTAR OFICIOS INFORMALES DE PRUEBA (creados por usuarios)
-- =============================================
INSERT INTO oficios_informales (usuario_id, numero_oficio, fecha_recepcion, asunto, canal, estado)
VALUES 
(2, 'INF-2025-001', '2025-03-01', 'Solicitud de información sobre trámite', 'WhatsApp', 'Pendiente'),
(3, 'INF-2025-002', '2025-03-05', 'Requerimiento de documentación', 'Email', 'Pendiente'),
(2, 'INF-2025-003', '2025-03-10', 'Consulta sobre estado de cuenta', 'Teléfono', 'Atendido');

-- =============================================
-- ACTUALIZAR AÑO DE OFICIOS
-- =============================================
UPDATE oficios SET año_oficio = EXTRACT(YEAR FROM fecha_oficio);

-- =============================================
-- VERIFICACIÓN
-- =============================================
SELECT '✅ ESQUEMA CREADO CORRECTAMENTE' AS mensaje;

SELECT 'USUARIOS:' AS tabla, COUNT(*) AS total FROM usuarios
UNION ALL
SELECT 'OFICIOS:', COUNT(*) FROM oficios
UNION ALL
SELECT 'OFICIOS_INFORMALES:', COUNT(*) FROM oficios_informales
UNION ALL
SELECT 'ARCHIVOS_BINARIOS:', COUNT(*) FROM archivos_binarios;

-- Mostrar usuarios
SELECT id, username, nombre_completo, es_admin FROM usuarios ORDER BY id;

-- Mostrar oficios formales
SELECT id, numero_oficio, estado, usuario_asignado_id FROM oficios ORDER BY id;

-- Mostrar oficios informales
SELECT id, usuario_id, numero_oficio, fecha_recepcion, asunto, canal, estado, fecha_respuesta 
FROM oficios_informales ORDER BY id;