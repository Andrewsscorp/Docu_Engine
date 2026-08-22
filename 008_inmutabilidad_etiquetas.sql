-- ==============================================================
-- 008_inmutabilidad_etiquetas.sql
-- Bloqueo de Inmutabilidad Forense y Auditoría
-- ==============================================================

-- 1. Tabla de Auditoría (Shadow Logging)
CREATE TABLE IF NOT EXISTS audit_rbac_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accion VARCHAR(100) NOT NULL,
    usuario_id UUID REFERENCES users(id) ON DELETE SET NULL,
    documento_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    ip_origen VARCHAR(45) NOT NULL,
    detalles JSONB,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Función Trigger
CREATE OR REPLACE FUNCTION trg_prevent_etiqueta_mutation()
RETURNS TRIGGER AS $$
DECLARE
    v_uso_count INT;
BEGIN
    -- Contar si la etiqueta ya está en uso
    SELECT COUNT(*) INTO v_uso_count 
    FROM documento_etiquetas 
    WHERE id_etiqueta = NEW.id_etiqueta;

    IF v_uso_count > 0 THEN
        -- Si hay uso, bloqueamos el UPDATE a nivel de motor
        RAISE EXCEPTION 'INTEGRIDAD_FORENSE: La etiqueta ya está asociada a documentos históricos y no puede ser alterada.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Asignación del Trigger SOLO a columnas específicas
DROP TRIGGER IF EXISTS trg_check_inmutabilidad_etiqueta ON etiquetas_maestras;

CREATE TRIGGER trg_check_inmutabilidad_etiqueta
BEFORE UPDATE OF nombre, color_fondo, color_texto, categoria
ON etiquetas_maestras
FOR EACH ROW
EXECUTE FUNCTION trg_prevent_etiqueta_mutation();

-- 4. Permisos
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE audit_rbac_logs TO docuengine_api;
