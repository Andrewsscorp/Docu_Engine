with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
@router.get("/expedientes/{expediente_id}/control_tipologias")
async def get_control_tipologias_view(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # Fetch Expediente
    exp_res = await db.execute(text("SELECT id, codigo_expediente, nombre_expediente, subserie_id, (estado = 'ABIERTO') as estado_abierto FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), 
                                {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_row = exp_res.fetchone()
    if not exp_row:
        return HTMLResponse("Expediente no encontrado", status_code=404)
    exp = dict(exp_row._mapping)
    
    # Execute Matrix LEFT JOIN
    matrix_res = await db.execute(text("""
        SELECT 
            t.id as tipologia_id, 
            t.codigo_tipologia,
            t.nombre as oficial, 
            t.formatos_permitidos,
            st.obligatoria,
            st.orden_sugerido,
            doc.id as documento_id,
            doc.file_name,
            doc.created_at as fecha_carga,
            doc.user_id as autor_carga,
            (CASE WHEN doc.id IS NOT NULL THEN 'CARGADO' ELSE 'FALTANTE' END) as estado_carga
        FROM agn_subserie_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id 
                  AND doc.agn_expediente_id = :eid 
                  AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        WHERE st.subserie_id = :sid
        ORDER BY st.obligatoria DESC, st.orden_sugerido ASC NULLS LAST, t.nombre ASC
    """), {"eid": expediente_id, "sid": exp["subserie_id"]})
    
    tipologias = []
    obligatorias = []
    opcionales = []
    completadas_req = 0
    total_req = 0
    
    for row in matrix_res.fetchall():
        t = dict(row._mapping)
        if t["fecha_carga"]:
            t["fecha_str"] = t["fecha_carga"].strftime("%d %b %Y, %H:%M")
        
        if t["obligatoria"]:
            total_req += 1
            if t["estado_carga"] == 'CARGADO':
                completadas_req += 1
            obligatorias.append(t)
        else:
            opcionales.append(t)
            
    completitud = int((completadas_req / total_req * 100)) if total_req > 0 else 100
    pendientes = total_req - completadas_req
    
    # 5. User's loose documents (for the modal linking)
    user_docs_res = await db.execute(text('''
        SELECT id, file_name 
        FROM documents 
        WHERE tenant_id = :t 
        AND status = 'COMPLETED' 
        AND agn_expediente_id IS NULL
        ORDER BY created_at DESC LIMIT 50
    '''), {"t": session_data["tenant_id"]})
    user_docs = [dict(r._mapping) for r in user_docs_res.fetchall()]

    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request=request, name="pages/control_tipologias.html", context={
        "request": request,
        "exp": exp,
        "obligatorias": obligatorias,
        "opcionales": opcionales,
        "completitud": completitud,
        "total_req": total_req,
        "completadas_req": completadas_req,
        "pendientes": pendientes,
        "user_docs": user_docs
    })
"""
content += new_endpoint

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
