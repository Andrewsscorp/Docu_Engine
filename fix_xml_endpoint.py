with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the timeline text
content = content.replace("elif ev[\"accion\"] == 'CERRAR_EXPEDIENTE': ev[\"accion_str\"] = \"Cierre de Expediente\"", "elif ev[\"accion\"] == 'CIERRE_EXPEDIENTE': ev[\"accion_str\"] = \"Cierre de Expediente\"")

# Add the endpoint
new_endpoint = """
@router.get("/expedientes/{expediente_id}/indice_xml")
async def descargar_indice_xml(
    expediente_id: str,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    res = await db.execute(text("SELECT indice_xml_path FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), {"eid": expediente_id, "t": session_data["tenant_id"]})
    row = res.fetchone()
    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="XML no encontrado")
        
    xml_path = row[0]
    import os
    if not os.path.exists(xml_path):
        raise HTTPException(status_code=404, detail="Archivo XML fisico no encontrado")
        
    from fastapi.responses import FileResponse
    return FileResponse(xml_path, media_type="application/xml", filename=f"{expediente_id}_indice_electronico.xml")

@router.get("/expedientes/{expediente_id}/exportar")
"""
content = content.replace("@router.get(\"/expedientes/{expediente_id}/exportar\")", new_endpoint)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
