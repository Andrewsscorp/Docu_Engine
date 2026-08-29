ALTER TABLE agn_dependencias DROP CONSTRAINT IF EXISTS agn_dependencias_estado_check;
UPDATE agn_dependencias SET estado = 'ABIERTO' WHERE estado = 'ACTIVA';
ALTER TABLE agn_dependencias ADD CONSTRAINT agn_dependencias_estado_check CHECK (estado IN ('ABIERTO', 'CERRADO'));
ALTER TABLE agn_dependencias ALTER COLUMN estado SET DEFAULT 'ABIERTO';

ALTER TABLE agn_dependencias ADD COLUMN IF NOT EXISTS fecha_cierre TIMESTAMP WITH TIME ZONE;
ALTER TABLE agn_dependencias ADD COLUMN IF NOT EXISTS soporte_cierre VARCHAR;
