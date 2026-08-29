CREATE TABLE IF NOT EXISTS agn_dependencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR NOT NULL,
    codigo VARCHAR NOT NULL,
    nombre VARCHAR NOT NULL,
    tipo VARCHAR NOT NULL CHECK (tipo IN ('FONDO', 'SECCION', 'SUBSECCION')),
    parent_id UUID REFERENCES agn_dependencias(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agn_series (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR NOT NULL,
    codigo VARCHAR NOT NULL,
    nombre VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agn_subseries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR NOT NULL,
    serie_id UUID NOT NULL REFERENCES agn_series(id) ON DELETE CASCADE,
    codigo VARCHAR NOT NULL,
    nombre VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agn_trd (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR NOT NULL,
    dependencia_id UUID NOT NULL REFERENCES agn_dependencias(id),
    serie_id UUID NOT NULL REFERENCES agn_series(id),
    subserie_id UUID REFERENCES agn_subseries(id),
    tiempo_gestion INT NOT NULL DEFAULT 0,
    tiempo_central INT NOT NULL DEFAULT 0,
    disposicion_final VARCHAR NOT NULL CHECK (disposicion_final IN ('CONSERVACION_TOTAL', 'ELIMINACION', 'SELECCION', 'MICROFILMACION_DIGITALIZACION')),
    estado_activa BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agn_expedientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR NOT NULL,
    trd_id UUID NOT NULL REFERENCES agn_trd(id),
    codigo_expediente VARCHAR NOT NULL UNIQUE,
    nombre_expediente VARCHAR NOT NULL,
    asunto TEXT,
    fecha_apertura TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_cierre TIMESTAMP WITH TIME ZONE,
    estado VARCHAR NOT NULL DEFAULT 'ABIERTO' CHECK (estado IN ('ABIERTO', 'CERRADO', 'TRANSFERIDO')),
    responsable_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agn_indice_electronico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expediente_id UUID NOT NULL REFERENCES agn_expedientes(id) ON DELETE CASCADE,
    documento_id UUID,
    accion VARCHAR NOT NULL,
    fecha_accion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_id VARCHAR NOT NULL,
    firma_indice VARCHAR,
    detalles JSONB
);

-- Adicionar columnas a documents si no existen
ALTER TABLE documents ADD COLUMN IF NOT EXISTS agn_expediente_id UUID REFERENCES agn_expedientes(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS folio INT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS hash_documento VARCHAR;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tipo_documental VARCHAR;

