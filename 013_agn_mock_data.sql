DO $$
DECLARE
    v_tenant VARCHAR;
    v_fondo UUID;
    v_seccion UUID;
    v_serie UUID;
    v_subserie UUID;
    v_trd UUID;
BEGIN
    SELECT tenant_id INTO v_tenant FROM tenant_settings LIMIT 1;
    IF v_tenant IS NULL THEN RETURN; END IF;
    
    -- Insert Fondo
    INSERT INTO agn_dependencias (tenant_id, codigo, nombre, tipo, parent_id)
    VALUES (v_tenant, 'ALC', 'Alcaldía de Tunja', 'FONDO', NULL)
    RETURNING id INTO v_fondo;
    
    -- Insert Seccion
    INSERT INTO agn_dependencias (tenant_id, codigo, nombre, tipo, parent_id)
    VALUES (v_tenant, 'SECED', 'Secretaría de Educación', 'SECCION', v_fondo)
    RETURNING id INTO v_seccion;
    
    -- Insert Serie
    INSERT INTO agn_series (tenant_id, codigo, nombre)
    VALUES (v_tenant, 'CON', 'Contratos')
    RETURNING id INTO v_serie;
    
    -- Insert Subserie
    INSERT INTO agn_subseries (tenant_id, serie_id, codigo, nombre)
    VALUES (v_tenant, v_serie, 'PS', 'Prestación de Servicios')
    RETURNING id INTO v_subserie;
    
    -- Insert TRD
    INSERT INTO agn_trd (tenant_id, dependencia_id, serie_id, subserie_id, tiempo_gestion, tiempo_central, disposicion_final)
    VALUES (v_tenant, v_seccion, v_serie, v_subserie, 2, 10, 'SELECCION')
    RETURNING id INTO v_trd;
    
END $$;
