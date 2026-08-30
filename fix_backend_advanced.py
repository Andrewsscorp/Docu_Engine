with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_post_block = r'class NuevaTipologiaPayload\(BaseModel\):.*?return JSONResponse\(\{.*?\}\, status_code=201\)'

new_post_block = """from typing import List

class NuevaTipologiaPayload(BaseModel):
    nombre_oficial: str
    soporte_origen: str
    formatos_permitidos: List[str]
    clasificacion: str
    exige_firma: bool

@router.post("/tipologias/diccionario")
async def post_crear_tipologia_diccionario(
    payload: NuevaTipologiaPayload,
    request: Request,
    session_data: dict = Depends(require_permission("tipologias:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    import json
    # Normalización estricta (Sanitización Semántica)
    nombre_limpio = payload.nombre_oficial.strip().upper()
    
    # Verificar si el nombre ya existe (Unicidad)
    exist_res = await db.execute(text("SELECT id FROM agn_tipologias WHERE nombre_oficial = :nom"), {"nom": nombre_limpio})
    if exist_res.fetchone():
        return JSONResponse({"status": "error", "message": "Ya existe una tipología con ese nombre oficial en el catálogo."}, status_code=409)
        
    res = await db.execute(text('''
        INSERT INTO agn_tipologias (
            nombre_oficial, soporte_origen, formatos_permitidos, 
            clasificacion, exige_firma, tenant_id, usuario_creador, estado_activo
        )
        VALUES (:nom, :sop, :form::jsonb, :clas, :firma, :t, :uid, TRUE)
        RETURNING id
    '''), {
        "nom": nombre_limpio,
        "sop": payload.soporte_origen,
        "form": json.dumps(payload.formatos_permitidos),
        "clas": payload.clasificacion,
        "firma": payload.exige_firma,
        "t": session_data["tenant_id"],
        "uid": session_data["user_id"]
    })
    
    nuevo_id = str(res.scalar())
    await db.commit()
    
    return JSONResponse({
        "status": "success", 
        "data": {
            "id": nuevo_id,
            "text": f"{nombre_limpio}"
        }
    }, status_code=201)"""

content = re.sub(old_post_block, new_post_block, content, flags=re.DOTALL)

# Also update the GET query to not use codigo_tipologia and change nombre to nombre_oficial
old_get_query = """        SELECT t.id, t.codigo_tipologia, t.nombre 
        FROM agn_tipologias t
        WHERE t.estado_activo = TRUE 
          AND t.tenant_id = :t
          AND t.id NOT IN (
              SELECT tipologia_id FROM agn_subserie_tipologia WHERE subserie_id = :sid AND estado_regla = TRUE
          )
        ORDER BY t.nombre ASC"""
        
new_get_query = """        SELECT t.id, t.nombre_oficial 
        FROM agn_tipologias t
        WHERE t.estado_activo = TRUE 
          AND t.tenant_id = :t
          AND t.id NOT IN (
              SELECT tipologia_id FROM agn_subserie_tipologia WHERE subserie_id = :sid AND estado_regla = TRUE
          )
        ORDER BY t.nombre_oficial ASC"""

content = content.replace(old_get_query, new_get_query)

# Update GET returning
old_get_ret = """return JSONResponse([{"id": str(t["id"]), "text": f"[{t['codigo_tipologia']}] {t['nombre']}" if t['codigo_tipologia'] else t['nombre']} for t in tipologias])"""
new_get_ret = """return JSONResponse([{"id": str(t["id"]), "text": t["nombre_oficial"]} for t in tipologias])"""

content = content.replace(old_get_ret, new_get_ret)

# Also update the matrix query in get_control_tipologias_view!
old_matrix_query = """        SELECT 
            t.id as tipologia_id, 
            t.codigo_tipologia,
            t.nombre as oficial,"""
new_matrix_query = """        SELECT 
            t.id as tipologia_id, 
            t.nombre_oficial as oficial,"""
content = content.replace(old_matrix_query, new_matrix_query)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
