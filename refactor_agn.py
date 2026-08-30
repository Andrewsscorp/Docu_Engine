with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

match = re.search(r'@router\.get\("/expedientes/module".*?return templates\.TemplateResponse\(request=request, name="components/expedientes_module\.html", context=context\)', content, re.DOTALL)

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
    
    # ---------------------------------------------------------
    # NIVEL 1: CARPETAS MAESTRAS (Si no hay subserie seleccionada)
    # ---------------------------------------------------------
    if not subserie_id and request.headers.get("hx-target") != "expedientes-results-grid" and request.headers.get("hx-target") != "expedientes-append-target":
        # Render the master folders view
        query_sub = '''
            SELECT ss.id, ss.codigo as subserie_codigo, ss.nombre as subserie_nombre,
                   s.codigo as serie_codigo, s.nombre as serie_nombre,
                   d.codigo as dep_codigo, d.nombre as dep_nombre,
                   ss.retencion_ag, ss.retencion_ac, ss.disposicion, ss.total_expedientes
            FROM agn_subseries ss
            JOIN agn_series s ON ss.serie_id = s.id
            JOIN agn_dependencias d ON s.seccion_id = d.id OR s.subseccion_id = d.id
            WHERE ss.tenant_id = :t
            ORDER BY d.codigo, s.codigo, ss.codigo
        '''
        res_sub = await db.execute(text(query_sub), {"t": tenant_id})
        carpetas = []
        for row in res_sub.fetchall():
            d = dict(row._mapping)
            d["codigo_jerarquico"] = f"{d['dep_codigo']}-{d['serie_codigo']}-{d['subserie_codigo']}"
            carpetas.append(d)
            
        total_folders = len(carpetas)
        return templates.TemplateResponse("components/subseries_module.html", {
            "request": request,
            "carpetas": carpetas,
            "total_folders": total_folders
        })

    # ---------------------------------------------------------
    # NIVEL 2: EXPEDIENTES (Interior de la Subserie)
    # ---------------------------------------------------------
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
    
    total_count = 0
    if is_filtered:
        count_query = f"SELECT COUNT(*) FROM agn_expedientes e WHERE {where_sql.replace('AND (e.created_at, e.id) < (CAST(:uf AS timestamp with time zone), CAST(:uid AS uuid))', '')}"
        res_count = await db.execute(text(count_query), {k: v for k, v in params.items() if k not in ['uf', 'uid', 'limit']})
        total_count = res_count.scalar()
    else:
        res_count = await db.execute(text("SELECT reltuples::bigint FROM pg_class WHERE relname = 'agn_expedientes'"))
        total_count = res_count.scalar() or 0
        
    # Fetch breadcrumbs context if inside a subserie
    breadcrumb = None
    if subserie_id:
        bc_query = '''
            SELECT ss.nombre as subserie_nombre, s.nombre as serie_nombre, d.nombre as dep_nombre
            FROM agn_subseries ss
            JOIN agn_series s ON ss.serie_id = s.id
            JOIN agn_dependencias d ON s.seccion_id = d.id OR s.subseccion_id = d.id
            WHERE ss.id = CAST(:subid AS uuid)
        '''
        res_bc = await db.execute(text(bc_query), {"subid": subserie_id})
        bc_row = res_bc.fetchone()
        if bc_row:
            bc = dict(bc_row._mapping)
            breadcrumb = f"Fondo > {bc['dep_nombre']} > {bc['serie_nombre']} > {bc['subserie_nombre']}"
    
    query_str = f'''
        SELECT e.id, e.codigo_expediente, e.nombre_expediente, e.fecha_apertura, e.estado_abierto, e.fase_archivo,
               e.cantidad_documentos as doc_count, e.soporte, e.created_at,
               u.username as responsable_nombre
        FROM agn_expedientes e
        LEFT JOIN users u ON e.responsable_id = CAST(u.id AS VARCHAR)
        WHERE {where_sql}
        ORDER BY e.created_at DESC, e.id DESC
        LIMIT :limit
    '''
    res = await db.execute(text(query_str), params)
    expedientes = [dict(r._mapping) for r in res.fetchall()]
    
    context = {
        "request": request, 
        "expedientes": expedientes,
        "total_count": total_count,
        "has_more": len(expedientes) == limit,
        "q": q, "status": status, "subserie_id": subserie_id,
        "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "soporte": soporte,
        "is_append": bool(ultimo_id),
        "breadcrumb": breadcrumb
    }
    
    # HTMX Target Check
    if request.headers.get("hx-target") == "expedientes-results-grid" or request.headers.get("hx-target") == "expedientes-append-target":
        template_name = "components/expedientes_grid_items.html" if request.headers.get("hx-target") == "expedientes-append-target" else "components/expedientes_grid.html"
        return templates.TemplateResponse(request=request, name=template_name, context=context)
        
    return templates.TemplateResponse(request=request, name="components/expedientes_module.html", context=context)
"""
    content = content.replace(match.group(0), new_func)
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced get_expedientes_module successfully.")
else:
    print("Regex failed to match.")
