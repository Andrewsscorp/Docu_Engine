import re

with open('app/routers/documents.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_routes = '''
import os
import uuid
import json
import asyncio
from werkzeug.utils import secure_filename
from fastapi import BackgroundTasks

# Mock OCR function as requested
async def iniciar_extraccion_ocr(document_id: str):
    # This simulates a background task taking time without blocking the main event loop
    await asyncio.sleep(2)
    # Here it would update the DB...
    print(f"OCR finished for {document_id}")

@router.post("/api/v1/documents/upload-initial", response_class=HTMLResponse)
async def upload_inicial_documento(
    request: Request,
    archivo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:subir"))
):
    tenant_id = session_data["tenant_id"]
    user_id = session_data["user_id"]
    
    # 1. Sanitization: secure_filename
    safe_name = secure_filename(archivo.filename)
    # Ensure it's safe and give it a unique UUID on disk
    file_ext = os.path.splitext(safe_name)[1]
    disk_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    upload_dir = os.path.join("uploads", str(tenant_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, disk_filename)
    
    content = await archivo.read()
    file_size = len(content)
    with open(file_path, "wb") as f:
        f.write(content)
        
    # 2. Insert into documents as DRAFT
    query = text("""
        INSERT INTO documents (id, tenant_id, file_name, file_path, uploaded_by, status, is_private)
        VALUES (:id, :t, :fn, :path, :uid, 'DRAFT', FALSE)
        RETURNING id
    """)
    doc_id = str(uuid.uuid4())
    await db.execute(query, {
        "id": doc_id,
        "t": tenant_id,
        "fn": safe_name,
        "path": disk_filename,
        "uid": user_id
    })
    await db.commit()
    
    # 3. Fetch tags, users, groups for the modal
    tags_res = await db.execute(text("SELECT id_etiqueta, nombre FROM etiquetas_maestras WHERE estado_activa = TRUE ORDER BY nombre"))
    etiquetas = tags_res.all()
    
    users_res = await db.execute(text("SELECT u.id, u.username, r.name as role_name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.tenant_id = :t AND u.id != :uid"), {"t": tenant_id, "uid": user_id})
    usuarios = users_res.all()
    
    groups_res = await db.execute(text("SELECT id, name FROM groups WHERE tenant_id = :t ORDER BY name"), {"t": tenant_id})
    grupos = groups_res.all()
    
    from app.main import templates
    return templates.TemplateResponse("modals/routing_modal.html", {
        "request": request,
        "document_id": doc_id,
        "document_name": safe_name,
        "etiquetas": etiquetas,
        "usuarios": usuarios,
        "grupos": grupos
    })

@router.post("/api/v1/documents/{documento_id}/finalize-routing")
async def finalizar_enrutamiento(
    documento_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    es_privado: bool = Form(False),
    etiqueta_id: str = Form(None),
    asignado_usuario_id: str = Form(None),
    asignado_grupo_id: str = Form(None),
    db: AsyncSession = Depends(get_db_session),
    session_data: dict = Depends(require_permission("documentos:subir"))
):
    tenant_id = session_data["tenant_id"]
    current_user_id = session_data["user_id"]
    
    async with db.begin():
        # Validate rules
        if not es_privado:
            if asignado_usuario_id == current_user_id:
                raise HTTPException(status_code=400, detail="Fallo de Integridad: No puede auto-asignarse un documento de revisión.")
            if not asignado_usuario_id and not asignado_grupo_id:
                raise HTTPException(status_code=400, detail="Debe asignar el documento a un usuario o grupo.")
                
        # 2. Update Document
        estado_nuevo = "PRIVADO" if es_privado else "OCR_PENDING"
        # Since group_id exists in our schema, but we added assigned_user_id
        await db.execute(text("""
            UPDATE documents 
            SET is_private = :priv, assigned_user_id = :u_id, group_id = :g_id, status = :estado
            WHERE id = :id AND tenant_id = :t
        """), {
            "priv": es_privado, 
            "u_id": asignado_usuario_id if asignado_usuario_id else None, 
            "g_id": asignado_grupo_id if asignado_grupo_id else None, 
            "estado": estado_nuevo, 
            "id": documento_id,
            "t": tenant_id
        })
        
        # 3. Assign Tag
        if etiqueta_id:
            await db.execute(text("INSERT INTO documento_etiquetas (id_documento, id_etiqueta) VALUES (:d_id, :e_id)"), 
                            {"d_id": documento_id, "e_id": etiqueta_id})
                            
        # 4. Shadow Logging & SLA Assignment
        if not es_privado:
            await db.execute(text("""
                INSERT INTO tasks_assignments (document_id, assigned_by, assigned_to, status)
                VALUES (:d_id, :por, :para, 'PENDING')
            """), {"d_id": documento_id, "por": current_user_id, "para": asignado_usuario_id})
            
            # NOVU trigger mock...
            
        # Shadow Log
        await db.execute(text("""
            INSERT INTO audit_rbac_logs (tenant_id, user_id, action, target_resource, target_id, ip_address, user_agent, details)
            VALUES (:t, :uid, 'DOCUMENTO_INGRESADO_Y_ENRUTADO', 'documents', :d_id, '127.0.0.1', 'System', :det)
        """), {
            "t": tenant_id,
            "uid": current_user_id,
            "d_id": str(documento_id),
            "det": json.dumps({"is_private": es_privado, "assigned_to": asignado_usuario_id})
        })
        
        # 5. Background Task
        if not es_privado:
            background_tasks.add_task(iniciar_extraccion_ocr, documento_id)
            
    response = HTMLResponse(content="")
    response.headers["HX-Trigger"] = json.dumps({"toastExito": {"mensaje": "Documento cargado y enrutado exitosamente."}})
    return response

'''
# Append new routes at the end of the file
with open('app/routers/documents.py', 'a', encoding='utf-8') as f:
    f.write(new_routes)
