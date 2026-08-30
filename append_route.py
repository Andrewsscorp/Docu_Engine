with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import_route = """
@router.post("/expedientes/{expediente_id}/importar_trd")
async def post_importar_trd_subserie(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    # 1. Obtener la subserie del expediente
    exp_res = await db.execute(text("SELECT subserie_id FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), 
                               {"eid": expediente_id, "t": session_data["tenant_id"]})
    exp_row = exp_res.fetchone()
    if not exp_row or not exp_row.subserie_id:
        return HTMLResponse("Expediente no encontrado o sin subserie asignada", status_code=404)
        
    # 2. Copiar tipologías de la subserie al expediente ignorando duplicados
    await db.execute(text('''
        INSERT INTO agn_expediente_tipologia (expediente_id, tipologia_id, obligatoria, orden_sugerido, usuario_creador)
        SELECT 
            :eid, 
            tipologia_id, 
            obligatoria, 
            orden_sugerido, 
            :uid
        FROM agn_subserie_tipologia
        WHERE subserie_id = :sid AND estado_regla = TRUE
        ON CONFLICT (expediente_id, tipologia_id) DO NOTHING
    '''), {
        "eid": expediente_id, 
        "sid": exp_row.subserie_id,
        "uid": session_data["user_id"]
    })
    
    await db.commit()
    
    # 3. Retornar la vista actualizada
    return await get_control_tipologias_view(expediente_id, request, session_data, db)
"""

if "post_importar_trd_subserie" not in content:
    content += import_route
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
        print("Route appended.")
else:
    print("Route already exists.")
