-- FASE 1: Actualización del Modelo de Datos para Ingestión y Enrutamiento

-- 1. Añadir columnas a la tabla documents (si no existen)
ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS assigned_user_id UUID REFERENCES users(id);

-- 2. Crear la tabla de asignaciones de tareas y SLA
CREATE TABLE IF NOT EXISTS tasks_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'PENDING',
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Crear índice para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks_assignments(assigned_to, status);
