-- Modificar esquemas de Tipología
ALTER TABLE agn_tipologias 
    ADD COLUMN IF NOT EXISTS codigo_tipologia VARCHAR(20),
    ADD COLUMN IF NOT EXISTS formatos_permitidos VARCHAR(50) DEFAULT 'PDF,XML',
    ADD COLUMN IF NOT EXISTS estado_activo BOOLEAN DEFAULT TRUE;

ALTER TABLE agn_subserie_tipologia
    ADD COLUMN IF NOT EXISTS orden_sugerido INT;

-- Agregar cantidad de páginas a los documentos
ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS paginas_cantidad INT DEFAULT 1;

-- 1. Trigger de Foliación Automática
CREATE OR REPLACE FUNCTION set_foliacion_automatica()
RETURNS TRIGGER AS $$
DECLARE
    v_max_folio INT;
    v_paginas INT;
BEGIN
    -- Interceptar vinculación a Expediente
    IF NEW.agn_expediente_id IS NOT NULL AND (TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND OLD.agn_expediente_id IS DISTINCT FROM NEW.agn_expediente_id)) THEN
        -- Calcular el máximo folio_fin estricto
        SELECT COALESCE(MAX(folio_fin), 0) INTO v_max_folio
        FROM documents 
        WHERE agn_expediente_id = NEW.agn_expediente_id;
        
        v_paginas := COALESCE(NEW.paginas_cantidad, 1);
        
        -- Imponer la matemática (sobrescribe cualquier intento del backend de enviar folios erróneos)
        NEW.folio := v_max_folio + 1;
        NEW.folio_fin := v_max_folio + v_paginas;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_documents_foliacion ON documents;
CREATE TRIGGER trg_documents_foliacion
BEFORE INSERT OR UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION set_foliacion_automatica();

-- 2. Trigger Anti-Fraude de Cierre TRD
CREATE OR REPLACE FUNCTION check_completitud_cierre()
RETURNS TRIGGER AS $$
DECLARE
    v_faltantes INT;
BEGIN
    -- Interceptar intento de cierre
    IF NEW.estado = 'CERRADO' AND (TG_OP = 'INSERT' OR OLD.estado != 'CERRADO') THEN
        -- Left Join Matricial Inmutable
        SELECT COUNT(*) INTO v_faltantes
        FROM agn_subserie_tipologia trd
        LEFT JOIN documents doc ON trd.tipologia_id = doc.tipologia_id 
              AND doc.agn_expediente_id = NEW.id
        WHERE trd.subserie_id = NEW.subserie_id 
          AND trd.obligatoria = TRUE
          AND doc.id IS NULL;
          
        IF v_faltantes > 0 THEN
            RAISE EXCEPTION 'Violación de Regla de Negocio (TRD): Expediente incompleto. Faltan % tipologias obligatorias para su cierre legal.', v_faltantes;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_expedientes_cierre ON agn_expedientes;
CREATE TRIGGER trg_expedientes_cierre
BEFORE UPDATE ON agn_expedientes
FOR EACH ROW EXECUTE FUNCTION check_completitud_cierre();
