with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
class NuevaTipologiaPayload(BaseModel):
    codigo: str
    nombre: str
    formatos: str

@router.post("/tipologias/diccionario")
async def post_crear_tipologia_diccionario(
    payload: NuevaTipologiaPayload,
    request: Request,
    session_data: dict = Depends(require_permission("tipologias:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    # Verificar si el código ya existe
    exist_res = await db.execute(text("SELECT id FROM agn_tipologias WHERE codigo_tipologia = :cod AND tenant_id = :t"), 
                                 {"cod": payload.codigo, "t": session_data["tenant_id"]})
    if exist_res.fetchone():
        return JSONResponse({"status": "error", "message": "Ya existe una tipología con ese código en el catálogo."}, status_code=409)
        
    res = await db.execute(text('''
        INSERT INTO agn_tipologias (codigo_tipologia, nombre, formatos_permitidos, tenant_id, estado_activo)
        VALUES (:cod, :nom, :form, :t, TRUE)
        RETURNING id
    '''), {
        "cod": payload.codigo,
        "nom": payload.nombre.upper(),
        "form": payload.formatos.upper(),
        "t": session_data["tenant_id"]
    })
    
    nuevo_id = str(res.scalar())
    await db.commit()
    
    return JSONResponse({
        "status": "success", 
        "data": {
            "id": nuevo_id,
            "text": f"[{payload.codigo}] {payload.nombre.upper()}"
        }
    }, status_code=201)
"""

content += new_endpoint

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
