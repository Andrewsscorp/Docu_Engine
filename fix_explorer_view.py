import re

with open('app/routers/documents.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the explorer_view signature and logic
old_explorer = '''@router.get("/api/v1/documents/explorer", response_class=HTMLResponse)
async def explorer_view(
    request: Request,
    q: str = "",
    sort: str = "desc",
    view: str = "cuadricula",
    group_id: str = "",
    status: str = "",
    page: int = 1,
    db: AsyncSession = Depends(get_db_session)
):
    uid, session_data, response = await require_permission(request, db, "documentos:leer")
    if not uid:
        return response
        
    tenant_id = session_data["tenant_id"]
    limit = 20
    offset = (page - 1) * limit
    
    # 1. Base Query
    query_str = """
        SELECT d.id, d.file_name, d.mime_type, d.file_size_bytes, d.status, d.created_at,
               g.name as group_name
        FROM documents d
        LEFT JOIN rbac_groups g ON d.group_id = g.id
        WHERE d.tenant_id = :t
    """
    params = {"t": tenant_id}
    
    if q:
        query_str += " AND d.fts_vector @@ plainto_tsquery('spanish', :q)"
        params["q"] = q
        
    if group_id:
        query_str += " AND d.group_id = :g"
        params["g"] = group_id
        
    if status:
        query_str += " AND d.status = :s"
        params["s"] = status
        
    # Enforce RLS visually (though pg policies do it too)
    user_roles = await get_role_hierarchy(db, uid)
    if "Admin" not in user_roles and "Auditor" not in user_roles:
        query_str += " AND (d.is_private = false OR d.uploaded_by = :u)"
        params["u"] = uid
        
    # Order and Pagination
    order_clause = " DESC" if sort == "desc" else " ASC"
    query_str += f" ORDER BY d.created_at {order_clause} LIMIT :l OFFSET :o"
    params["l"] = limit + 1
    params["o"] = offset
    
    result = await db.execute(text(query_str), params)
    docs_raw = result.fetchall()
    
    has_more = len(docs_raw) > limit
    docs_raw = docs_raw[:limit]
    
    docs = []
    for row in docs_raw:
        d = dict(row._mapping)
        docs.append(d)
        
    template_name = "components/explorer_results.html" if request.headers.get("hx-target") == "explorer-results" else "components/explorer.html"
    return templates.TemplateResponse(request=request, name=template_name, context={
        "request": request,
        "docs": docs,
        "page": page,
        "has_more": has_more,
        "sort": sort,
        "vista": view,
        "q": q
    })'''

new_explorer = '''@router.get("/api/v1/documents/explorer", response_class=HTMLResponse)
async def explorer_view(
    request: Request,
    q: str = "",
    sort: str = "desc",
    view: str = "cuadricula",
    group_id: str = "",
    status: str = "",
    page: int = 1,
    folder_filter: str = "",
    type_filter: str = "",
    date_filter: str = "",
    db: AsyncSession = Depends(get_db_session)
):
    uid, session_data, response = await require_permission(request, db, "documentos:leer")
    if not uid:
        return response
        
    tenant_id = session_data["tenant_id"]
    limit = 20
    offset = (page - 1) * limit
    
    # 1. Fetch Folders
    folders = []
    if request.headers.get("hx-target") != "explorer-results":
        f_res = await db.execute(
            text("SELECT f.id, f.name, f.color, (SELECT COUNT(id) FROM documents WHERE folder_id = f.id) as doc_count FROM folders f WHERE f.tenant_id = :t ORDER BY f.created_at DESC"),
            {"t": tenant_id}
        )
        for r in f_res.fetchall():
            folders.append(dict(r._mapping))
    
    # 2. Base Query
    query_str = """
        SELECT d.id, d.file_name, d.mime_type, d.file_size_bytes, d.status, d.created_at,
               g.name as group_name
        FROM documents d
        LEFT JOIN rbac_groups g ON d.group_id = g.id
        WHERE d.tenant_id = :t
    """
    params = {"t": tenant_id}
    
    if q:
        # Also match if q matches a folder name
        query_str += " AND (d.fts_vector @@ plainto_tsquery('spanish', :q) OR d.folder_id IN (SELECT id FROM folders WHERE name ILIKE :q_like AND tenant_id = :t))"
        params["q"] = q
        params["q_like"] = f"%{q}%"
        
    if folder_filter:
        query_str += " AND d.folder_id = :f"
        params["f"] = folder_filter
        
    if group_id:
        query_str += " AND d.group_id = :g"
        params["g"] = group_id
        
    if status:
        query_str += " AND d.status = :s"
        params["s"] = status
        
    if type_filter == "pdf":
        query_str += " AND d.mime_type ILIKE '%pdf%'"
    elif type_filter == "images":
        query_str += " AND d.mime_type ILIKE '%image%'"
        
    if date_filter == "week":
        query_str += " AND d.created_at >= NOW() - INTERVAL '7 days'"
    elif date_filter == "month":
        query_str += " AND d.created_at >= date_trunc('month', NOW())"
    elif date_filter == "year":
        query_str += " AND d.created_at >= date_trunc('year', NOW())"
        
    # Enforce RLS visually (though pg policies do it too)
    user_roles = await get_role_hierarchy(db, uid)
    if "Admin" not in user_roles and "Auditor" not in user_roles:
        query_str += " AND (d.is_private = false OR d.uploaded_by = :u)"
        params["u"] = uid
        
    # Order and Pagination
    order_clause = " DESC" if sort == "desc" else " ASC"
    query_str += f" ORDER BY d.created_at {order_clause} LIMIT :l OFFSET :o"
    params["l"] = limit + 1
    params["o"] = offset
    
    result = await db.execute(text(query_str), params)
    docs_raw = result.fetchall()
    
    has_more = len(docs_raw) > limit
    docs_raw = docs_raw[:limit]
    
    docs = []
    for row in docs_raw:
        d = dict(row._mapping)
        docs.append(d)
        
    template_name = "components/explorer_results.html" if request.headers.get("hx-target") == "explorer-results" else "components/explorer.html"
    return templates.TemplateResponse(request=request, name=template_name, context={
        "request": request,
        "docs": docs,
        "folders": folders,
        "page": page,
        "has_more": has_more,
        "sort": sort,
        "vista": view,
        "q": q,
        "type_filter": type_filter,
        "date_filter": date_filter
    })'''

content = content.replace(old_explorer, new_explorer)

with open('app/routers/documents.py', 'w', encoding='utf-8') as f:
    f.write(content)
