-- Migración 005: Auditoría Inmutable (Append-Only)
-- Este script crea una función de trigger que bloquea cualquier intento de UPDATE o DELETE
-- sobre las tablas de auditoría e historial del SGDEA, asegurando el No-Repudio forense.

CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        RAISE EXCEPTION 'Inmutabilidad Forense Activa: No se permite modificar registros de auditoria en la tabla %.', TG_TABLE_NAME;
    ELSIF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Inmutabilidad Forense Activa: No se permite borrar registros de auditoria en la tabla %.', TG_TABLE_NAME;
    END IF;
    RETURN NULL; -- Nunca se alcanza, pero requerido por sintaxis
END;
$$ LANGUAGE plpgsql;

-- 1. log_auditoria_sgdea
DROP TRIGGER IF EXISTS trg_append_only_log_auditoria_sgdea ON log_auditoria_sgdea;
CREATE TRIGGER trg_append_only_log_auditoria_sgdea
BEFORE UPDATE OR DELETE ON log_auditoria_sgdea
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

-- 2. audit_rbac_logs
DROP TRIGGER IF EXISTS trg_append_only_audit_rbac_logs ON audit_rbac_logs;
CREATE TRIGGER trg_append_only_audit_rbac_logs
BEFORE UPDATE OR DELETE ON audit_rbac_logs
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

-- 3. folder_audit_logs
DROP TRIGGER IF EXISTS trg_append_only_folder_audit_logs ON folder_audit_logs;
CREATE TRIGGER trg_append_only_folder_audit_logs
BEFORE UPDATE OR DELETE ON folder_audit_logs
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

-- 4. agn_indice_electronico (Manifiestos y firmas base)
DROP TRIGGER IF EXISTS trg_append_only_agn_indice_electronico ON agn_indice_electronico;
CREATE TRIGGER trg_append_only_agn_indice_electronico
BEFORE UPDATE OR DELETE ON agn_indice_electronico
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

-- 5. agn_auditoria_parametros (Cambios en TRDs y Metadatos Maestros)
DROP TRIGGER IF EXISTS trg_append_only_agn_auditoria_parametros ON agn_auditoria_parametros;
CREATE TRIGGER trg_append_only_agn_auditoria_parametros
BEFORE UPDATE OR DELETE ON agn_auditoria_parametros
FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

