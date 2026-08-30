ALTER TABLE agn_subserie_tipologia
    ADD COLUMN IF NOT EXISTS estado_regla BOOLEAN DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS usuario_creador UUID;

-- 1. Trigger de Auto-Secuencia
CREATE OR REPLACE FUNCTION trg_orden_visualizacion_trd_func()
RETURNS TRIGGER AS $$
DECLARE
    v_max_orden INT;
BEGIN
    IF NEW.orden_sugerido IS NULL THEN
        SELECT COALESCE(MAX(orden_sugerido), 0) INTO v_max_orden
        FROM agn_subserie_tipologia
        WHERE subserie_id = NEW.subserie_id;
        
        NEW.orden_sugerido := v_max_orden + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_orden_visualizacion_trd_insert ON agn_subserie_tipologia;
CREATE TRIGGER trg_orden_visualizacion_trd_insert
BEFORE INSERT ON agn_subserie_tipologia
FOR EACH ROW EXECUTE FUNCTION trg_orden_visualizacion_trd_func();

-- 2. Trigger Recálculo Retroactivo
-- (Placeholder conceptual, ya que el estado se calcula On-The-Fly en nuestra app)
-- Si la base de datos tuviese una tabla "estados_completitud", se invalidaría aquí.
