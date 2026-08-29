ALTER TABLE agn_expedientes
DROP CONSTRAINT IF EXISTS agn_expedientes_trd_id_fkey,
DROP COLUMN IF EXISTS trd_id,
ADD COLUMN IF NOT EXISTS fondo_id UUID NOT NULL REFERENCES agn_dependencias(id),
ADD COLUMN IF NOT EXISTS seccion_id UUID NOT NULL REFERENCES agn_dependencias(id),
ADD COLUMN IF NOT EXISTS subseccion_id UUID REFERENCES agn_dependencias(id),
ADD COLUMN IF NOT EXISTS serie_id UUID NOT NULL REFERENCES agn_series(id),
ADD COLUMN IF NOT EXISTS subserie_id UUID REFERENCES agn_subseries(id),
ADD COLUMN IF NOT EXISTS anio INT NOT NULL DEFAULT extract(year from current_date),
ADD COLUMN IF NOT EXISTS consecutivo INT NOT NULL DEFAULT 1;
