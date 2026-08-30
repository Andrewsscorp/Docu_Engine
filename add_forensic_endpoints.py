with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Insert the BackgroundTask import and AsyncSessionLocal
if "BackgroundTasks" not in content:
    content = content.replace("from fastapi import APIRouter, Depends, Request", "from fastapi import APIRouter, Depends, Request, BackgroundTasks")
    content = content.replace("from app.database import get_db_session", "from app.database import get_db_session, AsyncSessionLocal")
    content = content.replace("from fastapi.responses import HTMLResponse, JSONResponse", "from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse")

new_endpoints = """
import io
import zipfile
import tempfile
from fastapi.responses import StreamingResponse

# Tarea asíncrona para registrar la auditoría forense sin bloquear al usuario
async def log_audit_sgdea_async(expediente_id: str, usuario_id: str, tipo_evento: str, ip_origen: str, payload_legal: dict):
    import json
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text('''
                INSERT INTO log_auditoria_sgdea (id_expediente, id_usuario, tipo_evento, ip_origen, payload_legal)
                VALUES (:eid, :uid, :tev, :ip, :payload::jsonb)
            '''), {
                "eid": expediente_id,
                "uid": usuario_id,
                "tev": tipo_evento,
                "ip": ip_origen,
                "payload": json.dumps(payload_legal)
            })
            await session.commit()
    except Exception as e:
        print(f"Error asíncrono en log_audit_sgdea_async: {e}")

@router.get("/expedientes/{expediente_id}/exportar")
async def get_exportar_expediente_dip(
    expediente_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("expedientes:exportar")),
    db: AsyncSession = Depends(get_db_session)
):
    import hashlib
    # Verificar existencia y permisos
    exp_res = await db.execute(text("SELECT codigo_expediente, nombre_expediente, estado FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), 
                               {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_row = exp_res.fetchone()
    if not exp_row:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
        
    exp_code = exp_row.codigo_expediente
    
    # Obtener documentos
    docs_res = await db.execute(text('''
        SELECT d.id, d.file_name, d.file_path, d.file_hash, d.status, t.nombre_oficial 
        FROM documents d
        LEFT JOIN agn_tipologias t ON d.tipologia_id = t.id
        WHERE d.agn_expediente_id = :eid AND d.status IN ('COMPLETED', 'ARCHIVED')
        ORDER BY d.folio ASC
    '''), {"eid": expediente_id})
    docs = docs_res.fetchall()
    
    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        metadata = []
        for d in docs:
            d_dict = dict(d._mapping)
            if os.path.exists(d_dict["file_path"]):
                # Write to zip
                zip_file.write(d_dict["file_path"], arcname=f"documentos/{d_dict['file_name']}")
                metadata.append(d_dict)
                
        # Escribir metadatos
        zip_file.writestr("metadata_control.json", json.dumps(metadata, default=str, indent=2))
        
        # Obtener ultimo XML
        idx_res = await db.execute(text("SELECT * FROM agn_indice_electronico WHERE expediente_id = :eid ORDER BY fecha_accion DESC LIMIT 1"), {"eid": expediente_id})
        idx = idx_res.fetchone()
        if idx:
            xml_content = f"<?xml version='1.0'?><indice><hash_estado>{idx.firma_indice}</hash_estado></indice>" # Mock simple
            zip_file.writestr("indice_electronico.xml", xml_content)
            
    # Registrar auditoria
    ip_origen = request.client.host if request.client else "unknown"
    background_tasks.add_task(log_audit_sgdea_async, expediente_id, session_data["user_id"], "EXPORTACION_EXPEDIENTE", ip_origen, {"total_docs": len(docs)})
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=DIP_{exp_code}.zip"}
    )

@router.get("/documentos/{doc_id}/descargar_forense")
async def get_descargar_documento_forense(
    doc_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    import os
    doc_res = await db.execute(text("SELECT agn_expediente_id, file_path, file_name, file_hash FROM documents WHERE id = :did AND tenant_id = :t"), 
                               {"did": doc_id, "t": session_data["tenant_id"]})
    doc_row = doc_res.fetchone()
    if not doc_row or not doc_row.file_path or not os.path.exists(doc_row.file_path):
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
        
    def iterfile():
        with open(doc_row.file_path, mode="rb") as file_like:
            yield from file_like

    if doc_row.agn_expediente_id:
        ip_origen = request.client.host if request.client else "unknown"
        background_tasks.add_task(log_audit_sgdea_async, str(doc_row.agn_expediente_id), session_data["user_id"], "DESCARGA_FISICA", ip_origen, {"hash_sha256": doc_row.file_hash, "file": doc_row.file_name})

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={doc_row.file_name}"}
    )

@router.get("/documentos/{doc_id}/ver_forense")
async def get_ver_documento_forense(
    doc_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    import os
    doc_res = await db.execute(text("SELECT agn_expediente_id, file_path, file_name, file_hash, folio FROM documents WHERE id = :did AND tenant_id = :t"), 
                               {"did": doc_id, "t": session_data["tenant_id"]})
    doc_row = doc_res.fetchone()
    if not doc_row or not doc_row.file_path or not os.path.exists(doc_row.file_path):
        raise HTTPException(status_code=404, detail="Binario no encontrado en storage")
        
    def iterfile():
        with open(doc_row.file_path, mode="rb") as file_like:
            yield from file_like

    if doc_row.agn_expediente_id:
        ip_origen = request.client.host if request.client else "unknown"
        background_tasks.add_task(log_audit_sgdea_async, str(doc_row.agn_expediente_id), session_data["user_id"], "VISUALIZACION_DOC", ip_origen, {"folio_iniciado": doc_row.folio})

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={doc_row.file_name}"}
    )

"""

content += new_endpoints

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
