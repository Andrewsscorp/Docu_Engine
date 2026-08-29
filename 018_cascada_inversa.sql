
CREATE OR REPLACE FUNCTION trg_agn_dependencias_prevent_closure()
RETURNS TRIGGER AS $$
DECLARE
    active_children_count INT;
BEGIN
    -- Only check if we are transitioning from ABIERTO to CERRADO
    IF NEW.estado = 'CERRADO' AND OLD.estado = 'ABIERTO' THEN
        -- Check if it's a SECCION trying to close, and has active SUBSECCIONES
        IF OLD.tipo = 'SECCION' THEN
            SELECT COUNT(*) INTO active_children_count 
            FROM agn_dependencias 
            WHERE parent_id = OLD.id AND tipo = 'SUBSECCION' AND estado = 'ABIERTO';
            
            IF active_children_count > 0 THEN
                RAISE EXCEPTION 'Cascada Inversa Prohibida: No se puede liquidar la Sección porque tiene % Subsecciones activas. Liquide primero los grupos de trabajo.', active_children_count;
            END IF;
        END IF;
        
        -- Also check if it's a FONDO trying to close, and has active SECCIONES
        IF OLD.tipo = 'FONDO' THEN
            SELECT COUNT(*) INTO active_children_count 
            FROM agn_dependencias 
            WHERE parent_id = OLD.id AND tipo = 'SECCION' AND estado = 'ABIERTO';
            
            IF active_children_count > 0 THEN
                RAISE EXCEPTION 'Cascada Inversa Prohibida: No se puede liquidar el Fondo porque tiene % Secciones activas.', active_children_count;
            END IF;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_dependencia_closure ON agn_dependencias;

CREATE TRIGGER trg_prevent_dependencia_closure
BEFORE UPDATE OF estado ON agn_dependencias
FOR EACH ROW
EXECUTE FUNCTION trg_agn_dependencias_prevent_closure();
