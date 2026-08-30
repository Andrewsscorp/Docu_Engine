-- 1. Alterar agn_expedientes para agregar topografía y soporte
ALTER TABLE agn_expedientes ADD COLUMN IF NOT EXISTS soporte VARCHAR(50) DEFAULT 'ELECTRÓNICO';
ALTER TABLE agn_expedientes ADD COLUMN IF NOT EXISTS id_ubicacion_fisica UUID;

-- 2. Añadir el CHECK CONSTRAINT
ALTER TABLE agn_expedientes DROP CONSTRAINT IF EXISTS chk_topografia_soporte;
ALTER TABLE agn_expedientes ADD CONSTRAINT chk_topografia_soporte 
    CHECK ((soporte = 'ELECTRÓNICO' AND id_ubicacion_fisica IS NULL) OR (soporte IN ('FÍSICO', 'HÍBRIDO') AND id_ubicacion_fisica IS NOT NULL));

-- 3. Crear tablas de FUID
CREATE TABLE IF NOT EXISTS fuid_transferencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subserie_id UUID NOT NULL,
    consecutivo_oficial VARCHAR(50) UNIQUE NOT NULL,
    fecha_generacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_firmante UUID NOT NULL,
    hash_sha256 VARCHAR(64) NOT NULL,
    id_certificado_pki UUID, -- Nullable for now since we are simulating
    ruta_almacenamiento_pdf VARCHAR(255) NOT NULL,
    estado_transferencia VARCHAR(30) DEFAULT 'COMPLETADA',
    tenant_id VARCHAR(50) NOT NULL,
    
    CONSTRAINT fk_fuid_subserie FOREIGN KEY (subserie_id) REFERENCES agn_subseries(id),
    CONSTRAINT fk_fuid_usuario FOREIGN KEY (usuario_firmante) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS fuid_expedientes_vinculados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fuid_id UUID NOT NULL,
    expediente_id UUID NOT NULL,
    orden_consecutivo INT NOT NULL,
    
    CONSTRAINT uk_fuid_expediente UNIQUE (fuid_id, expediente_id),
    CONSTRAINT fk_vinculo_fuid FOREIGN KEY (fuid_id) REFERENCES fuid_transferencias(id),
    CONSTRAINT fk_vinculo_expediente FOREIGN KEY (expediente_id) REFERENCES agn_expedientes(id)
);

-- 4. Trigger de inmutabilidad
CREATE OR REPLACE FUNCTION trg_prevent_fuid_alteration()
RETURNS TRIGGER AS $$
DECLARE
    v_hash VARCHAR;
BEGIN
    SELECT hash_sha256 INTO v_hash FROM fuid_transferencias WHERE id = OLD.fuid_id;
    IF v_hash IS NOT NULL THEN
        RAISE EXCEPTION 'Violación de Inmutabilidad: No se puede alterar un FUID que ya posee firma criptográfica (SHA-256).';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fuid_vinculos_inmutables ON fuid_expedientes_vinculados;
CREATE TRIGGER trg_fuid_vinculos_inmutables
BEFORE UPDATE OR DELETE ON fuid_expedientes_vinculados
FOR EACH ROW EXECUTE FUNCTION trg_prevent_fuid_alteration();
