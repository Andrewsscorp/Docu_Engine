import re

with open('app/routers/documents.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I need to add folder endpoints
folder_endpoints = '''
@router.post("/api/v1/folders")
async def create_folder(
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
):
    uid, session_data, response = await require_permission(request, db, "documentos:subir")
    if not uid:
        return response
    
    tenant_id = session_data["tenant_id"]
    form_data = await request.form()
    name = form_data.get("name")
    color = form_data.get("color", "#4648d4")
    
    if not name:
        return JSONResponse({"status": "error", "message": "Nombre requerido"}, status_code=400)
        
    try:
        res = await db.execute(
            text("INSERT INTO folders (tenant_id, name, color, created_by) VALUES (:t, :n, :c, :u) RETURNING id"),
            {"t": tenant_id, "n": name, "c": color, "u": uid}
        )
        folder_id = res.scalar()
        
        await db.execute(
            text("INSERT INTO folder_audit_logs (folder_id, action, user_id, details) VALUES (:f, 'CREAR_CARPETA', :u, :d)"),
            {"f": folder_id, "u": uid, "d": '{"name": "' + name + '"}'}
        )
        await db.commit()
        return JSONResponse({"status": "success", "folder_id": str(folder_id)})
    except Exception as e:
        await db.rollback()
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.post("/api/v1/documentos/{doc_id}/mover")
async def move_document(
    doc_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    uid, session_data, response = await require_permission(request, db, "documentos:editar")
    if not uid:
        return response
        
    form_data = await request.form()
    folder_id = form_data.get("folder_id")
    
    try:
        # Verify document exists and belongs to tenant
        doc_res = await db.execute(text("SELECT id FROM documents WHERE id = :d AND tenant_id = :t"), {"d": doc_id, "t": session_data["tenant_id"]})
        if not doc_res.scalar():
            return JSONResponse({"status": "error", "message": "Documento no encontrado"}, status_code=404)
            
        await db.execute(text("UPDATE documents SET folder_id = :f WHERE id = :d"), {"f": folder_id if folder_id else None, "d": doc_id})
        
        if folder_id:
            await db.execute(
                text("INSERT INTO folder_audit_logs (folder_id, action, user_id, details) VALUES (:f, 'MOVER_DOCUMENTO', :u, :d)"),
                {"f": folder_id, "u": uid, "d": '{"doc_id": "' + doc_id + '"}'}
            )
            
        await db.commit()
        
        return HTMLResponse(content='<script>Swal.fire({toast: true, position: "top-end", icon: "success", title: "Documento movido", showConfirmButton: false, timer: 2000}); setTimeout(()=>htmx.trigger("body", "reloadExplorer"), 1000);</script>', headers={"HX-Trigger": "reloadExplorer"})
    except Exception as e:
        await db.rollback()
        return HTMLResponse(f"<script>Swal.fire('Error', 'No se pudo mover: {str(e)}', 'error');</script>")
'''

content = content + folder_endpoints

with open('app/routers/documents.py', 'w', encoding='utf-8') as f:
    f.write(content)
