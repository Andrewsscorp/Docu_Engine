with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_exp = '''@router.post("/expedientes")
async def create_agn_expediente(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    return JSONResponse({"status": "success", "message": "Expediente electrónico creado y registrado en el índice."})'''

new_exp = '''@router.post("/expedientes")
async def create_agn_expediente(
    request: Request,
    fondo_id: str = Form(...),
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    # LÓGICA NORMATIVA ARCHIVÍSTICA: Bloqueo Estructural (Write Lock)
    # Verificar que el Fondo esté ABIERTO antes de permitir la creación de un expediente
    q_fondo = text("SELECT estado FROM agn_dependencias WHERE id = :id AND tipo = 'FONDO'")
    res = await db.execute(q_fondo, {"id": fondo_id})
    estado_fondo = res.scalar()
    
    if estado_fondo == 'CERRADO':
        raise HTTPException(status_code=403, detail="Violación Normativa: El Fondo Documental se encuentra CERRADO (Acumulado). Está estrictamente prohibido por el AGN generar nuevos expedientes bajo esta raíz.")
        
    return JSONResponse({"status": "success", "message": "Expediente electrónico creado y registrado en el índice."})'''

content = content.replace(old_exp, new_exp)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
