-- ==============================================================
-- 007_gobernanza_etiquetas.sql
-- Evolución a Consola de Gobernanza Paramétrica (Categorías y Roles)
-- ==============================================================

-- 1. Añadir Categoría a la tabla principal
-- NOTA TÉCNICA: Si el negocio requiere una nueva familia (Ej: 'Riesgo Financiero'), 
-- ejecutar un ALTER TABLE DROP CONSTRAINT chk_etiqueta_categoria y recrearlo.
ALTER TABLE etiquetas_maestras 
ADD COLUMN IF NOT EXISTS categoria VARCHAR(30) DEFAULT 'Estado';

ALTER TABLE etiquetas_maestras 
DROP CONSTRAINT IF EXISTS chk_etiqueta_categoria;

ALTER TABLE etiquetas_maestras 
ADD CONSTRAINT chk_etiqueta_categoria CHECK (categoria IN ('Estado', 'Clasificación', 'Prioridad'));

-- Actualizar las etiquetas semilla existentes para que tengan categoría 'Estado'
UPDATE etiquetas_maestras SET categoria = 'Estado' WHERE categoria IS NULL;

-- 2. Nueva tabla para Control de Acceso Granular (RBAC por etiqueta)
CREATE TABLE IF NOT EXISTS etiqueta_roles_permitidos (
    id_etiqueta UUID NOT NULL REFERENCES etiquetas_maestras(id_etiqueta) ON DELETE CASCADE,
    id_rol UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (id_etiqueta, id_rol)
);

-- 3. Otorgar permisos al rol de API
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE etiqueta_roles_permitidos TO docuengine_api;
