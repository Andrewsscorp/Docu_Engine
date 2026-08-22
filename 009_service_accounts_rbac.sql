-- FASE 2: IMPLEMENTACIÓN DE SERVICE ACCOUNTS
ALTER TABLE users ADD COLUMN IF NOT EXISTS es_cuenta_servicio BOOLEAN DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS api_keys_servicio (
    id SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    fecha_expiracion TIMESTAMP,
    estado_activa BOOLEAN DEFAULT TRUE
);

-- FASE 3: TAXONOMÍA DE ROLES DE IA (RBAC)
-- Insert roles if they don't exist
INSERT INTO roles (name, hierarchy_level, tenant_id) 
SELECT 'svc_extractor_ocr', 90, (SELECT id FROM tenants LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'svc_extractor_ocr');

INSERT INTO roles (name, hierarchy_level, tenant_id) 
SELECT 'svc_analista_forense', 90, (SELECT id FROM tenants LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'svc_analista_forense');

INSERT INTO roles (name, hierarchy_level, tenant_id) 
SELECT 'svc_orquestador_workflow', 90, (SELECT id FROM tenants LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'svc_orquestador_workflow');

-- Insert service account users
INSERT INTO users (id, username, hash_password, role_id, es_cuenta_servicio, tenant_id) 
SELECT gen_random_uuid(), 'svc.extractor@docuengine.local', 'N/A', (SELECT id FROM roles WHERE name = 'svc_extractor_ocr' LIMIT 1), TRUE, (SELECT id FROM tenants LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'svc.extractor@docuengine.local');

INSERT INTO users (id, username, hash_password, role_id, es_cuenta_servicio, tenant_id) 
SELECT gen_random_uuid(), 'svc.analista@docuengine.local', 'N/A', (SELECT id FROM roles WHERE name = 'svc_analista_forense' LIMIT 1), TRUE, (SELECT id FROM tenants LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'svc.analista@docuengine.local');

INSERT INTO users (id, username, hash_password, role_id, es_cuenta_servicio, tenant_id) 
SELECT gen_random_uuid(), 'svc.orquestador@docuengine.local', 'N/A', (SELECT id FROM roles WHERE name = 'svc_orquestador_workflow' LIMIT 1), TRUE, (SELECT id FROM tenants LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'svc.orquestador@docuengine.local');

