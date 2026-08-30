with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """async def vincular_documento_expediente(
    expediente_id: str,
    documento_id: str = Form(...),
    tipologia_id: str = Form(...),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import fitz"""

new = """async def vincular_documento_expediente(
    expediente_id: str,
    documento_id: str = Form(...),
    tipologia_id: str = Form(...),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import fitz
    
    if tipologia_id == "ANEXO":
        tipologia_id = None"""

content = content.replace(old, new)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
