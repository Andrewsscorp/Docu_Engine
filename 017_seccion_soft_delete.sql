
CREATE OR REPLACE FUNCTION trg_agn_dependencias_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE agn_dependencias
    SET estado = 'CERRADO'
    WHERE id = OLD.id;
    
    -- Returning NULL cancels the actual DELETE operation on the table
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_soft_delete_dependencias ON agn_dependencias;

CREATE TRIGGER trg_soft_delete_dependencias
BEFORE DELETE ON agn_dependencias
FOR EACH ROW
EXECUTE FUNCTION trg_agn_dependencias_soft_delete();
