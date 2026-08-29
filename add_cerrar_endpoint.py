from fastapi import APIRouter
with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
from pydantic import BaseModel
from typing import Optional

class CerrarFondoRequest(BaseModel):
    fecha_cierre: str
    soporte_cierre: str

@router.put("/fondos/{fondo_id}/cerrar")
async def cerrar_fondo(
    fondo_id: str,
    payload: CerrarFondoRequest,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    ip_address = request.client.host if request.client else "unknown"
    
    # Verify the fondo exists and is currently open
    q_check = text("SELECT id, estado FROM agn_dependencias WHERE id = :id AND tipo = 'FONDO' AND tenant_id = :t")
    res = await db.execute(q_check, {"id": fondo_id, "t": tenant_id})
    fondo = res.fetchone()
    
    if not fondo:
        raise HTTPException(status_code=404, detail="Fondo no encontrado.")
    if fondo[1] == 'CERRADO':
        raise HTTPException(status_code=400, detail="El fondo ya se encuentra cerrado.")
        
    # Perform the closure
    q_update = text('''
        UPDATE agn_dependencias 
        SET estado = 'CERRADO', fecha_cierre = :fecha::timestamp, soporte_cierre = :soporte 
        WHERE id = :id
    ''')
    await db.execute(q_update, {
        "fecha": payload.fecha_cierre,
        "soporte": payload.soporte_cierre,
        "id": fondo_id
    })
    
    # Audit Logging for this critical action
    audit_q = text('''
        INSERT INTO audit_rbac_logs (accion, usuario_id, ip_origen, detalles)
        VALUES (:accion, :user_id, :ip, :detalles)
    ''')
    await db.execute(audit_q, {
        "accion": "CERRAR_FONDO_AGN",
        "user_id": user_id,
        "ip": ip_address,
        "detalles": json.dumps({"fondo_id": fondo_id, "fecha_cierre": payload.fecha_cierre, "soporte": payload.soporte_cierre})
    })
    
    await db.commit()
    
    return JSONResponse({"status": "success", "message": "El Fondo Documental ha sido clausurado legalmente y preservado."})
"""
if "/fondos/{fondo_id}/cerrar" not in content:
    with open("app/routers/agn.py", "a", encoding="utf-8") as f:
        f.write(new_endpoint)
