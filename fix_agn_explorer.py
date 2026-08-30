with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

start = -1
end = -1

for i, line in enumerate(lines):
    if "@router.get(\"/expedientes/explorer\")" in line:
        start = i
    if start != -1 and "return HTMLResponse" in line:
        end = i
        break

if start != -1 and end != -1:
    new_func = """@router.get("/expedientes/module", response_class=HTMLResponse)
async def get_expedientes_module(
    request: Request,
    q: str = "",
    status: str = "",
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    
    tenant_id = session_data["tenant_id"]
    
    # Query with filters
    query_str = '''
        SELECT e.id, e.codigo_expediente, e.nombre_expediente, e.fecha_apertura, (e.estado = 'ABIERTO') as estado_abierto,
               (SELECT COUNT(d.id) FROM documents d WHERE d.agn_expediente_id = e.id) as doc_count
        FROM agn_expedientes e
        WHERE e.tenant_id = :t
    '''
    params = {"t": tenant_id}
    
    if q:
        query_str += " AND (e.codigo_expediente ILIKE :q OR e.nombre_expediente ILIKE :q)"
        params["q"] = f"%{q}%"
        
    if status == 'abierto':
        query_str += " AND e.estado = 'ABIERTO'"
    elif status == 'cerrado':
        query_str += " AND e.estado = 'CERRADO'"
        
    query_str += " ORDER BY e.created_at DESC"
    
    res = await db.execute(text(query_str), params)
    expedientes = [dict(row._mapping) for row in res.fetchall()]
    
    # Check if requested just the grid (htmx search) or the full module
    if request.headers.get("hx-target") == "expedientes-results-grid":
        return templates.TemplateResponse(
            request=request, 
            name="components/expedientes_grid.html", 
            context={"expedientes": expedientes}
        )
    
    # Full module response
    return templates.TemplateResponse(
        request=request, 
        name="components/expedientes_module.html", 
        context={"request": request, "expedientes": expedientes, "q": q, "status": status}
    )
"""
    lines[start:end+1] = [new_func]
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Replaced!")
else:
    print("Not found!")
