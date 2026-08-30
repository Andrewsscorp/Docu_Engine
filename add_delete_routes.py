with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

delete_routes = """
@router.delete("/expedientes/{expediente_id}/tipologias/{tipologia_id}")
async def delete_expediente_tipologia(
    expediente_id: str,
    tipologia_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text('''
        DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid AND tipologia_id = :tid
    '''), {"eid": expediente_id, "tid": tipologia_id})
    await db.commit()
    return await get_control_tipologias_view(expediente_id, request, session_data, db)

@router.delete("/expedientes/{expediente_id}/tipologias")
async def delete_all_expediente_tipologias(
    expediente_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    await db.execute(text('''
        DELETE FROM agn_expediente_tipologia 
        WHERE expediente_id = :eid
    '''), {"eid": expediente_id})
    await db.commit()
    return await get_control_tipologias_view(expediente_id, request, session_data, db)
"""

if "delete_expediente_tipologia" not in content:
    content += delete_routes
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
        print("DELETE routes added.")
else:
    print("Routes already exist.")
