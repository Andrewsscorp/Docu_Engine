with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix in create_agn_fondo
bad_audit_1 = '''    audit_q = text(\"""
        INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles)
        VALUES (:accion, :user_id, :ip, :detalles)
    \""")
    await db.execute(audit_q, {
        "accion": "CREAR_FONDO_AGN",
        "user_id": user_id,
        "ip": ip_address,
        "detalles": json.dumps({"fondo_id": new_id, "codigo": codigo, "nombre": nombre, "estado": estado})
    })'''

good_audit_1 = '''    audit_q = text(\"""
        INSERT INTO audit_rbac_logs (tenant_id, action, performed_by_user_id, details)
        VALUES (:tenant, :action, :user_id, :details)
    \""")
    await db.execute(audit_q, {
        "tenant": tenant_id,
        "action": "CREAR_FONDO_AGN",
        "user_id": user_id,
        "details": json.dumps({"ip_origen": ip_address, "fondo_id": new_id, "codigo": codigo, "nombre": nombre, "estado": estado})
    })'''
content = content.replace(bad_audit_1, good_audit_1)

# Fix in cerrar_fondo
bad_audit_2 = '''    audit_q = text(\"""
        INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles)
        VALUES (:accion, :user_id, :ip, :detalles)
    \""")
    await db.execute(audit_q, {
        "accion": "CERRAR_FONDO_AGN",
        "user_id": user_id,
        "ip": ip_address,
        "detalles": json.dumps({"fondo_id": fondo_id, "fecha_cierre": payload.fecha_cierre, "soporte": payload.soporte_cierre})
    })'''

good_audit_2 = '''    audit_q = text(\"""
        INSERT INTO audit_rbac_logs (tenant_id, action, target_id, performed_by_user_id, details)
        VALUES (:tenant, :action, :target_id, :user_id, :details)
    \""")
    await db.execute(audit_q, {
        "tenant": tenant_id,
        "action": "CERRAR_FONDO_AGN",
        "target_id": fondo_id,
        "user_id": user_id,
        "details": json.dumps({"ip_origen": ip_address, "fecha_cierre": payload.fecha_cierre, "soporte": payload.soporte_cierre})
    })'''
content = content.replace(bad_audit_2, good_audit_2)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
