-- 1. Tabla de Auditoría de Parámetros
CREATE TABLE IF NOT EXISTS agn_auditoria_parametros (
    id_auditoria UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_tipologia UUID NOT NULL,
    campo_modificado VARCHAR(50) NOT NULL,
    valor_anterior VARCHAR(255),
    valor_nuevo VARCHAR(255),
    usuario_modificador UUID,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Alterar la tabla agn_tipologias
ALTER TABLE agn_tipologias DROP COLUMN IF EXISTS codigo_tipologia;
ALTER TABLE agn_tipologias RENAME COLUMN nombre TO nombre_oficial;

-- Drop and recreate formatos_permitidos as JSONB
ALTER TABLE agn_tipologias DROP COLUMN IF EXISTS formatos_permitidos;
ALTER TABLE agn_tipologias ADD COLUMN formatos_permitidos JSONB NOT NULL DEFAULT '["PDF"]'::jsonb;

-- Add new columns
ALTER TABLE agn_tipologias 
    ADD COLUMN IF NOT EXISTS soporte_origen VARCHAR(30) NOT NULL DEFAULT 'ELECTRONICO_NATIVO',
    ADD COLUMN IF NOT EXISTS clasificacion VARCHAR(20) NOT NULL DEFAULT 'PUBLICA',
    ADD COLUMN IF NOT EXISTS exige_firma BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS usuario_creador UUID;

-- 3. Constraints y Check
ALTER TABLE agn_tipologias ADD CONSTRAINT uk_nombre_tipologia UNIQUE (nombre_oficial);
ALTER TABLE agn_tipologias ADD CONSTRAINT chk_soporte CHECK (soporte_origen IN ('ELECTRONICO_NATIVO', 'FISICO_DIGITALIZADO'));
ALTER TABLE agn_tipologias ADD CONSTRAINT chk_clasificacion CHECK (clasificacion IN ('PUBLICA', 'CLASIFICADA', 'RESERVADA'));

-- Indice GIN para JSONB
CREATE INDEX IF NOT EXISTS idx_formatos_permitidos ON agn_tipologias USING GIN (formatos_permitidos);

-- 4. Triggers de Seguridad Forense
-- A. Bloqueo de Borrado Físico
CREATE OR REPLACE FUNCTION trg_prevent_tipologia_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Prohibido borrar tipologías estructurales. Use inactivación lógica (estado_activo = FALSE).';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_tipologia_delete ON agn_tipologias;
CREATE TRIGGER prevent_tipologia_delete
BEFORE DELETE ON agn_tipologias
FOR EACH ROW EXECUTE FUNCTION trg_prevent_tipologia_delete();

-- B. Auditoría de Clasificación
CREATE OR REPLACE FUNCTION trg_audit_tipologia_clasificacion()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.clasificacion IS DISTINCT FROM NEW.clasificacion THEN
        INSERT INTO agn_auditoria_parametros (id_tipologia, campo_modificado, valor_anterior, valor_nuevo)
        VALUES (NEW.id, 'clasificacion', OLD.clasificacion, NEW.clasificacion);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_tipologia_clasificacion ON agn_tipologias;
CREATE TRIGGER audit_tipologia_clasificacion
AFTER UPDATE ON agn_tipologias
FOR EACH ROW EXECUTE FUNCTION trg_audit_tipologia_clasificacion();

-- C. Cascada Inversa de Inactivación
CREATE OR REPLACE FUNCTION trg_prevent_inactivacion_tipologia()
RETURNS TRIGGER AS $$
DECLARE
    v_en_uso BOOLEAN;
BEGIN
    IF NEW.estado_activo = FALSE AND OLD.estado_activo = TRUE THEN
        SELECT EXISTS (
            SELECT 1 FROM agn_subserie_tipologia 
            WHERE tipologia_id = NEW.id AND estado_regla = TRUE
        ) INTO v_en_uso;
        
        IF v_en_uso THEN
            RAISE EXCEPTION 'Integridad Referencial: No se puede inactivar una tipología que está vinculada como regla activa en una Matriz TRD.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prevent_inactivacion_tipologia ON agn_tipologias;
CREATE TRIGGER prevent_inactivacion_tipologia
BEFORE UPDATE ON agn_tipologias
FOR EACH ROW EXECUTE FUNCTION trg_prevent_inactivacion_tipologia();
