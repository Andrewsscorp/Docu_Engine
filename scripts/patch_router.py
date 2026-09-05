with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_get = """@router.get("/modal/fondo")
async def get_crear_fondo_modal(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear"))
):
    return templates.TemplateResponse("modals/crear_fondo.html", {
        "request": request,
        "tenant_id": session_data["tenant_id"]
    })

"""

new_post = """@router.post("/fondos")
async def create_agn_fondo(
    request: Request,
    codigo: str = Form(...),
    nombre: str = Form(...),
    acto_administrativo: str = Form(None),
    estado: str = Form(...),
    archivo_acto: UploadFile = File(None),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    from app.repositories.agn_repository import AGNRepository
    from app.services.agn_service import AGNService
    
    repo = AGNRepository(db, session_data["tenant_id"])
    service = AGNService(repo)
    
    new_id = await service.crear_fondo(
        codigo=codigo,
        nombre=nombre,
        acto_administrativo=acto_administrativo,
        archivo_acto=archivo_acto,
        estado=estado,
        user_id=session_data["user_id"],
        ip_address=request.client.host if request.client else "unknown"
    )
    
    await db.commit()
    return JSONResponse({"status": "success", "id": new_id})

"""

# Lines are 0-indexed in array.
# get_crear_fondo_modal: 461-574 (array index 460 to 573)
# create_agn_fondo: 575-636 (array index 574 to 635)
# Let's find exactly the line indexes to be safe.
idx_get = -1
idx_post = -1
idx_next = -1

for i, line in enumerate(lines):
    if line.startswith("@router.get(\"/modal/fondo\")"): idx_get = i
    elif line.startswith("@router.post(\"/fondos\")"): idx_post = i
    elif line.startswith("@router.put(\"/fondos/{fondo_id}/cerrar\")"): idx_next = i

if idx_get != -1 and idx_post != -1 and idx_next != -1:
    lines = lines[:idx_get] + [new_get, new_post] + lines[idx_next:]
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Patched agn.py successfully")
else:
    print(f"Could not find indices: {idx_get}, {idx_post}, {idx_next}")
