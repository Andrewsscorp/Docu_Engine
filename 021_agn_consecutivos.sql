CREATE TABLE IF NOT EXISTS agn_consecutivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR NOT NULL,
    seccion_id UUID NOT NULL REFERENCES agn_dependencias(id),
    serie_id UUID NOT NULL REFERENCES agn_series(id),
    subseccion_id UUID REFERENCES agn_dependencias(id),
    subserie_id UUID REFERENCES agn_subseries(id),
    anio INT NOT NULL,
    ultimo_consecutivo INT NOT NULL DEFAULT 0
);

ALTER TABLE agn_consecutivos
DROP CONSTRAINT IF EXISTS unique_consecutivo_rama,
ADD CONSTRAINT unique_consecutivo_rama UNIQUE NULLS NOT DISTINCT (tenant_id, seccion_id, serie_id, subseccion_id, subserie_id, anio);
