-- 1. Insertar Permiso de Exportación
INSERT INTO permissions (name, description) 
VALUES ('expedientes:exportar', 'Permite compilar y exportar el DIP (Paquete de Información de Difusión) del expediente incluyendo los binarios y el Índice XML.')
ON CONFLICT (name) DO NOTHING;

-- 2. Asignar permiso al rol SuperAdmin (asumiendo que su ID es la del tenant/setup original)
DO $$
DECLARE
    v_role_id UUID;
    v_perm_id UUID;
BEGIN
    SELECT id INTO v_role_id FROM roles WHERE name = 'SuperAdmin' LIMIT 1;
    SELECT id INTO v_perm_id FROM permissions WHERE name = 'expedientes:exportar' LIMIT 1;
    
    IF v_role_id IS NOT NULL AND v_perm_id IS NOT NULL THEN
        INSERT INTO role_permissions (role_id, permission_id) 
        VALUES (v_role_id, v_perm_id)
        ON CONFLICT DO NOTHING;
    END IF;
END $$;
