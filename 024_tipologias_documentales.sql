-- Catálogo Maestro de Tipologías Documentales
CREATE TABLE IF NOT EXISTS agn_tipologias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_tenant_tipologia UNIQUE (tenant_id, nombre)
);

-- Tabla Puente Relacional (Subserie <-> Tipología Obligatoria)
CREATE TABLE IF NOT EXISTS agn_subserie_tipologia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subserie_id UUID NOT NULL REFERENCES agn_subseries(id) ON DELETE CASCADE,
    tipologia_id UUID NOT NULL REFERENCES agn_tipologias(id) ON DELETE RESTRICT,
    obligatoria BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_subserie_tipologia UNIQUE (subserie_id, tipologia_id)
);

-- Alterar documents para taxonomía y foliación exacta
ALTER TABLE documents 
    ADD COLUMN tipologia_id UUID REFERENCES agn_tipologias(id),
    ADD COLUMN folio_fin INTEGER;

-- Rellenar algunas tipologías de ejemplo para el Tenant Dummy
INSERT INTO agn_tipologias (tenant_id, nombre, descripcion) VALUES
('22222222-2222-2222-2222-222222222222', 'Resolución', 'Acto administrativo de carácter general o particular.'),
('22222222-2222-2222-2222-222222222222', 'Acta', 'Documento que deja constancia de lo tratado y acordado en una reunión.'),
('22222222-2222-2222-2222-222222222222', 'Informe', 'Documento que describe el estado, avance o resultado de una actividad.'),
('22222222-2222-2222-2222-222222222222', 'Anexo', 'Documento adjunto que complementa la información del documento principal.'),
('22222222-2222-2222-2222-222222222222', 'Contrato', 'Acuerdo de voluntades que crea o transfiere derechos y obligaciones.')
ON CONFLICT DO NOTHING;
