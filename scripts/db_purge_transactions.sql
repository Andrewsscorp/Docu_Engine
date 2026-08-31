-- =============================================================================
-- SCRIPT DE PURGA TRANSACCIONAL (SANITIZATION) - PARTE 19
-- =============================================================================
-- Este script ELIMINA de forma segura todos los datos transaccionales 
-- (Expedientes, Documentos, Logs, Metadatos de búsqueda) generados durante
-- la etapa de desarrollo y pruebas, DEJANDO INTACTA la configuración maestra
-- (Usuarios, Roles, Permisos, Series, Subseries y Tipologías Documentales).
--
-- ADVERTENCIA: Ejecutar únicamente antes del pase a producción (Go-Live).
-- =============================================================================

BEGIN;

-- 1. Desactivar Triggers de Inmutabilidad temporalmente (para permitir borrar auditoría)
ALTER TABLE log_auditoria_sgdea DISABLE TRIGGER ALL;
ALTER TABLE audit_rbac_logs DISABLE TRIGGER ALL;
ALTER TABLE folder_audit_logs DISABLE TRIGGER ALL;
ALTER TABLE agn_indice_electronico DISABLE TRIGGER ALL;
ALTER TABLE agn_auditoria_parametros DISABLE TRIGGER ALL;

-- 2. Eliminar Transacciones Archivísticas (Expedientes y Documentos)
-- Se usa CASCADE si hay llaves foráneas apuntando a ellos.
TRUNCATE TABLE documents CASCADE;
TRUNCATE TABLE agn_expedientes CASCADE;
TRUNCATE TABLE agn_expediente_tipologia CASCADE;
TRUNCATE TABLE file_tags CASCADE;

-- 3. Eliminar Historial y Logs Transaccionales
TRUNCATE TABLE folder_audit_logs CASCADE;
TRUNCATE TABLE log_auditoria_sgdea CASCADE;
TRUNCATE TABLE audit_rbac_logs CASCADE;
TRUNCATE TABLE agn_indice_electronico CASCADE;

-- 4. Reactivar Triggers de Inmutabilidad
ALTER TABLE log_auditoria_sgdea ENABLE TRIGGER ALL;
ALTER TABLE audit_rbac_logs ENABLE TRIGGER ALL;
ALTER TABLE folder_audit_logs ENABLE TRIGGER ALL;
ALTER TABLE agn_indice_electronico ENABLE TRIGGER ALL;
ALTER TABLE agn_auditoria_parametros ENABLE TRIGGER ALL;

-- 5. Reiniciar secuencias de IDs (si aplica)
-- ALTER SEQUENCE documents_id_seq RESTART WITH 1; (Los UUID no requieren esto)

COMMIT;

-- 6. Reindexar y optimizar (Vacuum) para recuperar espacio en disco y optimizar índices FTS
VACUUM FULL ANALYZE;
