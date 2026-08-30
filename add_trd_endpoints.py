with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoints = """
@router.get("/subseries/{subserie_id}/modal_trd")
async def get_modal_trd(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    sub_res = await db.execute(text("SELECT * FROM agn_subseries WHERE id = :sid"), {"sid": subserie_id})
    sub = dict(sub_res.fetchone()._mapping)
    
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(request=request, name="components/modal_vincular_trd.html", context={
        "request": request,
        "subserie": sub
    })

@router.get("/subseries/{subserie_id}/tipologias/disponibles")
async def get_tipologias_disponibles(
    subserie_id: str,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    # Trae tipologías maestras que NO estén vinculadas a esta subserie
    res = await db.execute(text('''
        SELECT t.id, t.codigo_tipologia, t.nombre 
        FROM agn_tipologias t
        WHERE t.estado_activo = TRUE 
          AND t.tenant_id = :t
          AND t.id NOT IN (
              SELECT tipologia_id FROM agn_subserie_tipologia WHERE subserie_id = :sid AND estado_regla = TRUE
          )
        ORDER BY t.nombre ASC
    '''), {"t": session_data["tenant_id"], "sid": subserie_id})
    
    tipologias = [dict(r._mapping) for r in res.fetchall()]
    # Formatear para Select2 o frontend JSON:
    return JSONResponse([{"id": str(t["id"]), "text": f"[{t['codigo_tipologia']}] {t['nombre']}"} for t in tipologias])

class TRDLinkPayload(BaseModel):
    id_tipologia: str
    es_obligatorio: bool
    orden: Optional[int] = None

@router.post("/subseries/{subserie_id}/tipologias")
async def post_vincular_trd(
    subserie_id: str,
    payload: TRDLinkPayload,
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    # Validar si ya existe
    exist_res = await db.execute(text("SELECT id FROM agn_subserie_tipologia WHERE subserie_id = :sid AND tipologia_id = :tid"), {"sid": subserie_id, "tid": payload.id_tipologia})
    if exist_res.fetchone():
        return JSONResponse({"status": "error", "message": "Esta tipología ya pertenece a la Subserie."}, status_code=409)
        
    await db.execute(text('''
        INSERT INTO agn_subserie_tipologia (subserie_id, tipologia_id, obligatoria, orden_sugerido, usuario_creador)
        VALUES (:sid, :tid, :obl, :ord, :uid)
    '''), {
        "sid": subserie_id,
        "tid": payload.id_tipologia,
        "obl": payload.es_obligatorio,
        "ord": payload.orden,
        "uid": session_data["user_id"]
    })
    
    # Log Auditoria (opcional aquí si lo centralizamos)
    await db.commit()
    return JSONResponse({"status": "success"}, status_code=201)
"""
content += new_endpoints

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
