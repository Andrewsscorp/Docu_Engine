with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()
import re

content = re.sub(r'INSERT INTO audit_rbac_logs \(accion, usuario_id, ip_origen, detalles\)\s+VALUES \(:accion, :user_id, :ip, :detalles\)', 
    'INSERT INTO audit_rbac_logs (tenant_id, action, target_id, performed_by_user_id, details)\\n        VALUES (:tenant, :action, :target_id, :user_id, :details)', content)

content = re.sub(r'"accion": "CERRAR_FONDO_AGN",\s+"user_id": user_id,\s+"ip": ip_address,\s+"detalles": json.dumps\(\{"fondo_id": fondo_id, "fecha_cierre": payload.fecha_cierre, "soporte": payload.soporte_cierre\}\)',
    '"tenant": tenant_id,\\n        "action": "CERRAR_FONDO_AGN",\\n        "target_id": fondo_id,\\n        "user_id": user_id,\\n        "details": json.dumps({"ip_origen": ip_address, "fecha_cierre": payload.fecha_cierre, "soporte": payload.soporte_cierre})', content)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
