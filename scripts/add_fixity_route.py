with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    docs = f.read()

import_stmt = "from app.services.fixity_service import FixityService\n"
if "FixityService" not in docs:
    docs = docs.replace("router = APIRouter()", "router = APIRouter()\n" + import_stmt)

new_route = """

@router.post("/fixity")
async def trigger_fixity_check(
    background_tasks: BackgroundTasks,
    session_data: dict = Depends(require_permission("documentos:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    # Desplegar a una tarea de fondo (Scrubbing puede tardar varios minutos u horas en volumen)
    background_tasks.add_task(FixityService.run_fixity_check, session_data["tenant_id"], db, session_data["user_id"])
    return {"status": "success", "detail": "Fixity Check programado exitosamente en segundo plano. Los resultados se registrarán en la auditoría inmutable."}
"""

if "@router.post(\"/fixity\")" not in docs:
    docs += new_route

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(docs)
