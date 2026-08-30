sql = """
CREATE TABLE IF NOT EXISTS agn_expediente_tipologia (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    expediente_id UUID NOT NULL REFERENCES agn_expedientes(id) ON DELETE CASCADE,
    tipologia_id UUID NOT NULL REFERENCES agn_tipologias(id) ON DELETE RESTRICT,
    obligatoria BOOLEAN DEFAULT TRUE,
    orden_sugerido INT,
    estado_regla BOOLEAN DEFAULT TRUE,
    usuario_creador VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(expediente_id, tipologia_id)
);

CREATE OR REPLACE FUNCTION trg_orden_visualizacion_exp_trd_func()
RETURNS TRIGGER AS $$
DECLARE
    v_max_orden INT;
BEGIN
    IF NEW.orden_sugerido IS NULL THEN
        SELECT COALESCE(MAX(orden_sugerido), 0) INTO v_max_orden
        FROM agn_expediente_tipologia
        WHERE expediente_id = NEW.expediente_id;
        
        NEW.orden_sugerido := v_max_orden + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_orden_visualizacion_exp_trd_insert ON agn_expediente_tipologia;
CREATE TRIGGER trg_orden_visualizacion_exp_trd_insert
BEFORE INSERT ON agn_expediente_tipologia
FOR EACH ROW EXECUTE FUNCTION trg_orden_visualizacion_exp_trd_func();

GRANT ALL PRIVILEGES ON agn_expediente_tipologia TO docuengine_api;
"""
with open("033_expediente_especifico_trd.sql", "w", encoding="utf-8") as f:
    f.write(sql)
