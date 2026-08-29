TRUNCATE TABLE agn_series CASCADE;

ALTER TABLE agn_series
ADD COLUMN IF NOT EXISTS fondo_id UUID REFERENCES agn_dependencias(id),
ADD COLUMN IF NOT EXISTS seccion_id UUID REFERENCES agn_dependencias(id),
ADD COLUMN IF NOT EXISTS subseccion_id UUID REFERENCES agn_dependencias(id),
ADD COLUMN IF NOT EXISTS retencion_ag INT NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS retencion_ac INT NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS disposicion CHAR(2) NOT NULL DEFAULT 'CT',
ADD COLUMN IF NOT EXISTS estado_activa BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE agn_series
DROP CONSTRAINT IF EXISTS unique_seccion_subseccion_codigo,
ADD CONSTRAINT unique_seccion_subseccion_codigo UNIQUE (seccion_id, subseccion_id, codigo) NULLS NOT DISTINCT;
