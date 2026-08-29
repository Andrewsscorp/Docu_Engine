ALTER TABLE agn_series
DROP CONSTRAINT IF EXISTS unique_seccion_subseccion_codigo,
ADD CONSTRAINT unique_seccion_subseccion_codigo UNIQUE NULLS NOT DISTINCT (seccion_id, subseccion_id, codigo);
