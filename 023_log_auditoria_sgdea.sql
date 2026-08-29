CREATE TABLE IF NOT EXISTS log_auditoria_sgdea (
    id_log UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_expediente UUID NOT NULL REFERENCES agn_expedientes(id) ON DELETE CASCADE,
    id_usuario VARCHAR NOT NULL,
    tipo_evento VARCHAR(50) NOT NULL,
    ip_origen VARCHAR(45) NOT NULL,
    payload_legal JSONB NOT NULL,
    fecha_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION trg_log_auditoria_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Violación Normativa Forense: La tabla de auditoría (log_auditoria_sgdea) es inmutable. Se prohíbe cualquier intento de UPDATE o DELETE sobre la evidencia legal de No Repudio.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_prevent_log_auditoria_modification ON log_auditoria_sgdea;
CREATE TRIGGER trigger_prevent_log_auditoria_modification
BEFORE UPDATE OR DELETE ON log_auditoria_sgdea
FOR EACH ROW EXECUTE FUNCTION trg_log_auditoria_immutable();
