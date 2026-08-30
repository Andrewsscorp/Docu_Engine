with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

new_put = """
@router.put("/expedientes/{id}")
async def update_expediente(
    id: str,
    request: Request,
    session_data: dict = Depends(require_permission("expedientes:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    form_data = await request.form()
    nombre = form_data.get("nombre_expediente")
    resp_id = form_data.get("responsable_id")
    
    tenant_id = session_data["tenant_id"]
    
    # Validation constraint
    res_check = await db.execute(text("SELECT estado_abierto, fase_archivo FROM agn_expedientes WHERE id = :id AND tenant_id = :t"), {"id": id, "t": tenant_id})
    row = res_check.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
        
    if not row.estado_abierto or row.fase_archivo == 'TRANSFERENCIA':
        return JSONResponse(status_code=403, content={"error": "Inmutabilidad Activa: No se puede modificar un expediente cerrado o en transferencia según Ley 527."})
        
    await db.execute(text("UPDATE agn_expedientes SET nombre_expediente = :n, responsable_id = :r WHERE id = :id"), {"n": nombre, "r": resp_id, "id": id})
    await db.commit()
    
    return {"status": "success"}
"""

content += new_put

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Added PUT /expedientes/{id}")
