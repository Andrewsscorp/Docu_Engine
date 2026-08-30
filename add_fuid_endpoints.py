with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We will inject the two endpoints right after get_fuid_subserie
new_endpoints = """
import hashlib
from datetime import datetime
from fastapi.responses import PlainTextResponse

@router.post("/subseries/{subserie_id}/fuid/firmar")
async def firmar_fuid(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # 1. Fetch data
        fallback_sql = '''
        SELECT exp.id as exp_id, exp.codigo_expediente, 
               COALESCE((SELECT SUM(paginas_cantidad) FROM documents doc WHERE doc.agn_expediente_id = exp.id AND doc.status IN ('COMPLETED', 'ARCHIVED')), 0) AS folios
        FROM agn_expedientes exp
        WHERE exp.estado = 'CERRADO' AND exp.subserie_id = :sid
        '''
        res = await db.execute(text(fallback_sql), {"sid": subserie_id})
        filas = res.fetchall()
        
        # 2. Check empty constraint
        exp_validos = []
        for r in filas:
            if r.folios > 0:
                exp_validos.append(r)
                
        if not exp_validos:
            return JSONResponse({"status": "error", "detail": "No hay expedientes con documentos validos en esta subserie para firmar."}, status_code=400)
            
        # 3. Simulate PDF generation & Hash
        content_to_hash = f"{subserie_id}-{session_data['user_id']}-{datetime.now().isoformat()}".encode('utf-8')
        fuid_hash = hashlib.sha256(content_to_hash).hexdigest()
        
        # 4. Insert Transferencia
        transf_res = await db.execute(text('''
            INSERT INTO fuid_transferencias (subserie_id, consecutivo_oficial, usuario_firmante, hash_sha256, ruta_almacenamiento_pdf, tenant_id)
            VALUES (:sid, :consecutivo, :user_id, :hash, :ruta, :t)
            RETURNING id
        '''), {
            "sid": subserie_id, 
            "consecutivo": f"FUID-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": session_data["user_id"],
            "hash": fuid_hash,
            "ruta": f"/fuid_archives/{fuid_hash}.pdf",
            "t": session_data["tenant_id"]
        })
        fuid_id = transf_res.scalar()
        
        # 5. Insert Vinculos and Update expedientes
        for idx, exp in enumerate(exp_validos):
            await db.execute(text('''
                INSERT INTO fuid_expedientes_vinculados (fuid_id, expediente_id, orden_consecutivo)
                VALUES (:fid, :eid, :orden)
            '''), {"fid": fuid_id, "eid": exp.exp_id, "orden": idx + 1})
            
            await db.execute(text("UPDATE agn_expedientes SET estado = 'ARCHIVO_CENTRAL' WHERE id = :eid"), {"eid": exp.exp_id})
            
        # 6. Audit
        await db.execute(text('''
            INSERT INTO log_auditoria_sgdea (tenant_id, user_id, action, entity_type, entity_id, ip_address, user_agent, details)
            VALUES (:t, :u, 'FIRMA_FUID_TRANSFERENCIA', 'fuid', :fid, :ip, :ua, :det)
        '''), {
            "t": session_data["tenant_id"],
            "u": session_data["user_id"],
            "fid": str(fuid_id),
            "ip": request.client.host if request.client else "unknown",
            "ua": request.headers.get("user-agent", "unknown"),
            "det": f'{{"hash": "{fuid_hash}", "expedientes_vinculados": {len(exp_validos)}}}'
        })
        
        await db.commit()
        return JSONResponse({"status": "success", "hash": fuid_hash})
    except Exception as e:
        await db.rollback()
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

@router.get("/subseries/{subserie_id}/fuid/csv")
async def descargar_plana_fuid(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # Audit log first
    await db.execute(text('''
        INSERT INTO log_auditoria_sgdea (tenant_id, user_id, action, entity_type, entity_id, ip_address, user_agent, details)
        VALUES (:t, :u, 'EXPORTACION_METADATOS_PLANA', 'fuid_subserie', :sid, :ip, :ua, '{}')
    '''), {
        "t": session_data["tenant_id"],
        "u": session_data["user_id"],
        "sid": subserie_id,
        "ip": request.client.host if request.client else "unknown",
        "ua": request.headers.get("user-agent", "unknown")
    })
    await db.commit()
    
    # Just returning a dummy string for the file content
    csv_content = "NO_ORDEN,CODIGO,NOMBRE_UNIDAD,FECHA_INICIAL,FECHA_FINAL,CAJA_CARPETA,FOLIOS,SOPORTE\n"
    return PlainTextResponse(content=csv_content, headers={
        "Content-Disposition": f"attachment; filename=FUID_{subserie_id}_Plano.csv"
    })
"""

# Append to the end of file
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content + new_endpoints)
