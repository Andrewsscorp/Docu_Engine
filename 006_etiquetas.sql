-- ==============================================================
-- 006_etiquetas.sql
-- Taxonomía dinámica de etiquetas y permisos RBAC
-- ==============================================================

CREATE TABLE IF NOT EXISTS etiquetas_maestras (
    id_etiqueta UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(50) NOT NULL,
    color_fondo VARCHAR(30) NOT NULL,
    color_texto VARCHAR(30) NOT NULL,
    es_sistema BOOLEAN DEFAULT FALSE,
    creado_por UUID REFERENCES users(id) ON DELETE SET NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    estado_activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS documento_etiquetas (
    id_documento UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    id_etiqueta UUID NOT NULL REFERENCES etiquetas_maestras(id_etiqueta) ON DELETE RESTRICT,
    PRIMARY KEY (id_documento, id_etiqueta)
);

-- Insertar Permisos RBAC
INSERT INTO permissions (name, description) VALUES
('etiquetas:ver', 'Ver el listado de etiquetas y su uso'),
('etiquetas:editar', 'Crear y modificar etiquetas'),
('etiquetas:eliminar', 'Realizar soft-delete de etiquetas no de sistema')
ON CONFLICT (name) DO NOTHING;

-- Insertar Seed Data para el flujo de la firma (Solo si no existen)
INSERT INTO etiquetas_maestras (nombre, color_fondo, color_texto, es_sistema)
SELECT 'Para Revisión', 'bg-indigo-100', 'text-indigo-700', TRUE
WHERE NOT EXISTS (SELECT 1 FROM etiquetas_maestras WHERE nombre = 'Para Revisión');

INSERT INTO etiquetas_maestras (nombre, color_fondo, color_texto, es_sistema)
SELECT 'Para Corregir', 'bg-rose-100', 'text-rose-700', TRUE
WHERE NOT EXISTS (SELECT 1 FROM etiquetas_maestras WHERE nombre = 'Para Corregir');

INSERT INTO etiquetas_maestras (nombre, color_fondo, color_texto, es_sistema)
SELECT 'Devuelto', 'bg-amber-100', 'text-amber-700', TRUE
WHERE NOT EXISTS (SELECT 1 FROM etiquetas_maestras WHERE nombre = 'Devuelto');
