with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_func_pattern = r"@router\.get\(\"/expedientes/module\", response_class=HTMLResponse\).*?# Full module response.*?return templates\.TemplateResponse\([^)]+\)"

match = re.search(old_func_pattern, content, re.DOTALL)
if match:
    old_func = match.group(0)
    
    new_func = """@router.get("/expedientes/module", response_class=HTMLResponse)
async def get_expedientes_module(
    request: Request,
    q: str = "",
    status: str = "",
    fecha_inicio: str = "",
    fecha_fin: str = "",
    soporte: str = "",
    page: int = 1,
    limit: int = 15,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    
    tenant_id = session_data["tenant_id"]
    offset = (page - 1) * limit
    
    params = {"t": tenant_id}
    where_clauses = ["e.tenant_id = :t"]
    
    if q:
        # Full-text search with to_tsvector
        where_clauses.append("(to_tsvector('spanish', e.codigo_expediente || ' ' || e.nombre_expediente) @@ plainto_tsquery('spanish', :q))")
        params["q"] = q
        
    if status:
        if status == 'abierto':
            where_clauses.append("e.estado = 'ABIERTO'")
        elif status == 'cerrado':
            where_clauses.append("e.estado = 'CERRADO'")
        elif status == 'transferencia':
            where_clauses.append("e.fecha_transferencia_central IS NOT NULL")
            
    if fecha_inicio:
        where_clauses.append("e.fecha_apertura >= :fi::date")
        params["fi"] = fecha_inicio
        
    if fecha_fin:
        where_clauses.append("e.fecha_apertura <= :ff::date")
        params["ff"] = fecha_fin
        
    if soporte:
        where_clauses.append("e.soporte = :soporte")
        params["soporte"] = soporte
        
    where_sql = " AND ".join(where_clauses)
    
    # Get total count safely without scanning everything unless filters are applied
    # For large datasets, pg_class could be used, but since we are filtering, we do an exact count
    count_query = f"SELECT COUNT(*) FROM agn_expedientes e WHERE {where_sql}"
    res_count = await db.execute(text(count_query), params)
    total_count = res_count.scalar()
    
    # Query with filters and pagination
    query_str = f'''
        SELECT e.id, e.codigo_expediente, e.nombre_expediente, e.fecha_apertura, (e.estado = 'ABIERTO') as estado_abierto,
               (SELECT COUNT(d.id) FROM documents d WHERE d.agn_expediente_id = e.id) as doc_count,
               e.soporte
        FROM agn_expedientes e
        WHERE {where_sql}
        ORDER BY e.created_at DESC
        LIMIT :l OFFSET :o
    '''
    params["l"] = limit
    params["o"] = offset
    
    res = await db.execute(text(query_str), params)
    expedientes = [dict(row._mapping) for row in res.fetchall()]
    
    has_more = len(expedientes) == limit
    
    context = {
        "request": request, 
        "expedientes": expedientes, 
        "q": q, 
        "status": status,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "soporte": soporte,
        "page": page,
        "has_more": has_more,
        "total_count": total_count
    }
    
    # Check if requested just the grid (htmx search/pagination) or the full module
    if request.headers.get("hx-target") == "expedientes-results-grid" or request.headers.get("hx-target") == "expedientes-append-target":
        # If it's a "Cargar más", we append to the list
        template_name = "components/expedientes_grid_items.html" if request.headers.get("hx-target") == "expedientes-append-target" else "components/expedientes_grid.html"
        return templates.TemplateResponse(request=request, name=template_name, context=context)
    
    # Full module response
    return templates.TemplateResponse(request=request, name="components/expedientes_module.html", context=context)"""
    
    content = content.replace(old_func, new_func)
    
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced!")
else:
    print("Not found!")
