-- ==============================================================
-- 005_asignaciones_workflow.sql
-- Tabla transaccional para el Workflow de Asignaciones y SLA
-- ==============================================================

CREATE TABLE IF NOT EXISTS tareas_asignaciones (
    id_asignacion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_documento UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    asignado_por UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asignado_a UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    etiqueta_accion VARCHAR(100) NOT NULL, -- Ej: "Revisión Urgente", "Firma Requerida"
    fecha_asignacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tiempo_respuesta_esperado TIMESTAMP WITH TIME ZONE NOT NULL,
    estado_tarea VARCHAR(50) DEFAULT 'Pendiente', -- Pendiente, En Progreso, Completado, Vencido
    
    CONSTRAINT chk_estado_tarea CHECK (estado_tarea IN ('Pendiente', 'En Progreso', 'Completado', 'Vencido'))
);

-- Índices para búsqueda rápida de tareas por usuario
CREATE INDEX idx_tareas_asignado_a ON tareas_asignaciones(asignado_a);
CREATE INDEX idx_tareas_asignado_por ON tareas_asignaciones(asignado_por);
CREATE INDEX idx_tareas_documento ON tareas_asignaciones(id_documento);

-- Habilitar RLS (Row Level Security)
ALTER TABLE tareas_asignaciones ENABLE ROW LEVEL SECURITY;

-- Un usuario puede ver las tareas que le fueron asignadas, O las que él mismo asignó.
-- Los superadministradores pueden ver todo.
CREATE POLICY tareas_select_policy ON tareas_asignaciones FOR SELECT 
    USING (
        current_setting('app.is_superadmin', true) = 'true' OR
        asignado_a::text = current_setting('app.current_user_id', true) OR
        asignado_por::text = current_setting('app.current_user_id', true)
    );

CREATE POLICY tareas_insert_policy ON tareas_asignaciones FOR INSERT 
    WITH CHECK (
        current_setting('app.is_superadmin', true) = 'true' OR
        asignado_por::text = current_setting('app.current_user_id', true)
    );

CREATE POLICY tareas_update_policy ON tareas_asignaciones FOR UPDATE 
    USING (
        current_setting('app.is_superadmin', true) = 'true' OR
        asignado_a::text = current_setting('app.current_user_id', true) OR
        asignado_por::text = current_setting('app.current_user_id', true)
    );
