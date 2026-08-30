with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We will replace the entire get_expedientes_module function
match = re.search(r'@router\.get\("/expedientes/module".*?ORDER BY e\.created_at DESC\s+LIMIT :limit OFFSET :offset\s+''\),\s*params\)\s+rows = res\.fetchall\(\)\s+expedientes = \[dict\(r\._mapping\) for r in rows\]\s+return templates\.TemplateResponse\([^)]+\)', content, re.DOTALL)

if not match:
    # Alternative search
    match = re.search(r'@router\.get\("/expedientes/module".*?return templates\.TemplateResponse\([^)]+\)', content, re.DOTALL)

if match:
    new_func = """@router.get("/expedientes/module", response_class=HTMLResponse)
async def get_expedientes_module(
    request: Request,
    q: str = "",
    status: str = "",
    subserie_id: str = "",
    fecha_inicio: str = "",
    fecha_fin: str = "",
    soporte: str = "",
    ultimo_fecha: str = "",
    ultimo_id: str = "",
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    
    tenant_id = session_data["tenant_id"]
    limit = 12
    
    params = {"t": tenant_id, "limit": limit}
    where_clauses = ["e.tenant_id = :t"]
    
    is_filtered = bool(q or status or subserie_id or fecha_inicio or fecha_fin or soporte)
    
    if q:
        where_clauses.append("(to_tsvector('spanish', coalesce(e.codigo_expediente, '') || ' ' || coalesce(e.nombre_expediente, '')) @@ plainto_tsquery('spanish', :q))")
        params["q"] = q
        
    if status:
        if status == 'abierto':
            where_clauses.append("e.estado_abierto = TRUE")
        elif status == 'cerrado':
            where_clauses.append("e.estado_abierto = FALSE AND e.fase_archivo = 'GESTION'")
        elif status == 'transferencia':
            where_clauses.append("e.fase_archivo = 'TRANSFERENCIA'")
            
    if fecha_inicio and fecha_fin:
        where_clauses.append("e.fecha_apertura BETWEEN CAST(:fi AS timestamp with time zone) AND CAST(:ff AS timestamp with time zone)")
        params["fi"] = fecha_inicio + " 00:00:00"
        params["ff"] = fecha_fin + " 23:59:59"
        
    if soporte:
        where_clauses.append("e.soporte = :soporte")
        params["soporte"] = soporte
        
    if subserie_id:
        where_clauses.append("e.subserie_id = CAST(:subid AS uuid)")
        params["subid"] = subserie_id
        
    # Keyset Pagination
    if ultimo_fecha and ultimo_id:
        where_clauses.append("(e.created_at, e.id) < (CAST(:uf AS timestamp with time zone), CAST(:uid AS uuid))")
        params["uf"] = ultimo_fecha
        params["uid"] = ultimo_id
        
    where_sql = " AND ".join(where_clauses)
    
    # Global count using pg_class for un-filtered view to avoid scanning, exact count if filtered
    total_count = 0
    if is_filtered:
        count_query = f"SELECT COUNT(*) FROM agn_expedientes e WHERE {where_sql.replace('AND (e.created_at, e.id) < (CAST(:uf AS timestamp with time zone), CAST(:uid AS uuid))', '')}"
        res_count = await db.execute(text(count_query), {k: v for k, v in params.items() if k not in ['uf', 'uid', 'limit']})
        total_count = res_count.scalar()
    else:
        res_count = await db.execute(text("SELECT reltuples::bigint FROM pg_class WHERE relname = 'agn_expedientes'"))
        total_count = res_count.scalar() or 0
        
    # Fetch subseries for the dropdown
    res_sub = await db.execute(text("SELECT id, codigo, nombre FROM agn_subseries WHERE tenant_id = :t ORDER BY codigo"), {"t": tenant_id})
    subseries = [dict(r._mapping) for r in res_sub.fetchall()]
    
    # Optimized query loading relations
    query_str = f'''
        SELECT e.id, e.codigo_expediente, e.nombre_expediente, e.fecha_apertura, e.estado_abierto, e.fase_archivo,
               e.cantidad_documentos as doc_count, e.soporte, e.created_at,
               u.nombres || ' ' || u.apellidos as responsable_nombre
        FROM agn_expedientes e
        LEFT JOIN usuarios u ON e.responsable_id = CAST(u.id AS VARCHAR)
        WHERE {where_sql}
        ORDER BY e.created_at DESC, e.id DESC
        LIMIT :limit
    '''
    res = await db.execute(text(query_str), params)
    rows = res.fetchall()
    expedientes = [dict(r._mapping) for r in rows]
    
    return templates.TemplateResponse("pages/expedientes_module.html", {
        "request": request, 
        "expedientes": expedientes,
        "subseries": subseries,
        "total_count": total_count,
        "has_more": len(expedientes) == limit,
        "q": q, "status": status, "subserie_id": subserie_id,
        "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "soporte": soporte,
        "is_append": bool(ultimo_id)
    })
    
@router.post("/expedientes/{id}/cierre")
async def post_cierre_expediente(
    id: str,
    session_data: dict = Depends(require_permission("expedientes:editar")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    res = await db.execute(text("UPDATE agn_expedientes SET estado_abierto = FALSE, fecha_cierre = CURRENT_TIMESTAMP WHERE id = :id AND tenant_id = :t RETURNING id"), {"id": id, "t": tenant_id})
    if not res.scalar():
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    await db.commit()
    return {"status": "success", "detail": "Expediente sellado correctamente (Inmutabilidad Activada)"}
"""
    content = content.replace(match.group(0), new_func)
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced get_expedientes_module successfully.")
else:
    print("Could not find the function block via regex.")
