import re

with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn = f.read()

import_stmt = "from app.services.expediente_service import ExpedienteService\n"
if import_stmt not in agn:
    agn = agn.replace("from fastapi import APIRouter", "from fastapi import APIRouter\n" + import_stmt)

# Match the old function exactly
old_func_pattern = r"(?s)(@router\.post\(\"/expedientes/\{expediente_id\}/cerrar\"\)\nasync def cerrar_expediente\(.*?return JSONResponse\(\{\"status\": \"success\", \"xml_hash\": raw_hash\}\)\n)"

new_func = """@router.post("/expedientes/{expediente_id}/cerrar")
async def cerrar_expediente(
    expediente_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    ip_origen = request.client.host if request.client else "unknown"
    result = await ExpedienteService.cerrar_expediente(
        expediente_id=expediente_id,
        tenant_id=session_data["tenant_id"],
        user_id=session_data["user_id"],
        ip_origen=ip_origen,
        db=db,
        background_tasks=background_tasks
    )
    return JSONResponse(result)
"""
new_agn, count = re.subn(old_func_pattern, new_func, agn)
if count == 0:
    print("Warning: regex replacement failed!")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(new_agn)
print(f"Replaced {count} instances.")
