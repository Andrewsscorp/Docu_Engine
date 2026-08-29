ALTER TABLE agn_dependencias ADD COLUMN IF NOT EXISTS acto_administrativo VARCHAR;
ALTER TABLE agn_dependencias ADD COLUMN IF NOT EXISTS archivo_acto_url VARCHAR;
ALTER TABLE agn_dependencias ADD COLUMN IF NOT EXISTS estado VARCHAR NOT NULL DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'SUPRIMIDA', 'FUSIONADA'));

CREATE UNIQUE INDEX IF NOT EXISTS idx_dependencias_fondo_uk ON agn_dependencias (tenant_id, codigo) WHERE parent_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_dependencias_hijos_uk ON agn_dependencias (tenant_id, parent_id, codigo) WHERE parent_id IS NOT NULL;
